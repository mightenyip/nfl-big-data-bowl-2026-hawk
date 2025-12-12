"""
Ball Release Detection Module

This module identifies when the quarterback releases the ball based on the
data structure: Ball Release Frame = max(input_frame) - num_frames_output
"""

import pandas as pd
import numpy as np


def get_ball_release_frames(tracking_data):
    """
    Calculate ball release frame for each play.
    
    Formula: ball_release_frame = max(input_frame_id) - num_frames_output
    
    This assumes:
    - Input data contains frames from snap through ball release + reaction period
    - num_frames_output tells us how many frames of reaction data we have
    - Ball release occurs before the reaction period starts
    
    Args:
        tracking_data: DataFrame with columns ['play_id', 'frame_id', 'num_frames_output']
        
    Returns:
        DataFrame with columns ['play_id', 'ball_release_frame', 'max_input_frame', 'num_output_frames']
    """
    play_info = tracking_data.groupby('play_id').agg({
        'frame_id': 'max',
        'num_frames_output': 'first'
    }).reset_index()
    
    play_info.columns = ['play_id', 'max_input_frame', 'num_output_frames']
    play_info['ball_release_frame'] = (
        play_info['max_input_frame'] - play_info['num_output_frames']
    )
    
    # Filter out invalid calculations
    play_info = play_info[play_info['ball_release_frame'] >= 1]
    
    return play_info


def validate_ball_release(play_data, ball_release_frame, ball_land_x, ball_land_y):
    """
    Validate ball release frame by checking for reaction indicators.
    
    Indicators:
    1. Defensive players turn toward ball landing point after release
    2. QB shows throw pattern (planted before, movement after)
    3. General activity increase after release
    
    Args:
        play_data: DataFrame with player tracking data for one play
        ball_release_frame: Hypothesized ball release frame
        ball_land_x: Ball landing X coordinate
        ball_land_y: Ball landing Y coordinate
        
    Returns:
        Dictionary with validation indicators and overall score
    """
    indicators = {
        'defense_turns_toward_ball': 0,
        'qb_throw_pattern': 0,
        'activity_increase': 0
    }
    
    def calculate_angle_to_target(x, y, target_x, target_y):
        """Calculate angle from player position to target in degrees"""
        dx = target_x - x
        dy = target_y - y
        angle = np.arctan2(dy, dx) * 180 / np.pi
        return angle
    
    # Indicator 1: Defensive players turn toward ball
    defense = play_data[play_data['player_side'] == 'Defense'].copy()
    defense_turned = 0
    
    for player_id in defense['nfl_id'].unique():
        player_data = defense[defense['nfl_id'] == player_id].sort_values('frame_id')
        
        if len(player_data) < 5:
            continue
        
        # Calculate angles to ball landing point
        player_data['angle_to_ball'] = calculate_angle_to_target(
            player_data['x'], player_data['y'], ball_land_x, ball_land_y
        )
        player_data['dir_error'] = abs(player_data['dir'] - player_data['angle_to_ball'])
        player_data['dir_error'] = player_data['dir_error'].apply(
            lambda x: min(x, 360 - x)  # Normalize to 0-180 degrees
        )
        
        pre = player_data[player_data['frame_id'] <= ball_release_frame]
        post = player_data[player_data['frame_id'] > ball_release_frame]
        
        if len(pre) > 1 and len(post) > 1:
            pre_error = pre['dir_error'].mean()
            post_error = post['dir_error'].mean()
            
            # If error decreases, player is turning toward ball
            if post_error < pre_error * 0.9:
                defense_turned += 1
    
    if defense_turned >= 1:
        indicators['defense_turns_toward_ball'] = 1
    
    # Indicator 2: QB throw pattern
    qb = play_data[play_data['player_position'] == 'QB'].sort_values('frame_id')
    if len(qb) > ball_release_frame + 2:
        pre_qb = qb[qb['frame_id'] <= ball_release_frame]
        
        if len(pre_qb) > 3:
            x_std = pre_qb['x'].std()
            speed_avg = pre_qb['s'].mean()
            
            # QB should be relatively planted before throw
            if x_std < 1.0 and speed_avg < 2.0:
                indicators['qb_throw_pattern'] = 1
    
    # Indicator 3: Activity increase
    all_players = play_data.copy()
    all_players_sorted = all_players.sort_values(['nfl_id', 'frame_id'])
    
    pre_activity = []
    post_activity = []
    
    for player_id in all_players_sorted['nfl_id'].unique():
        player_data = all_players_sorted[all_players_sorted['nfl_id'] == player_id].sort_values('frame_id')
        
        if len(player_data) < 5:
            continue
        
        player_data['accel_mag'] = abs(player_data['a'])
        
        pre = player_data[player_data['frame_id'] <= ball_release_frame]
        post = player_data[player_data['frame_id'] > ball_release_frame]
        
        if len(pre) > 1 and len(post) > 1:
            pre_activity.append(pre['accel_mag'].mean())
            post_activity.append(post['accel_mag'].mean())
    
    if len(pre_activity) > 0 and len(post_activity) > 0:
        if np.mean(post_activity) > np.mean(pre_activity) * 1.1:
            indicators['activity_increase'] = 1
    
    indicators['total_score'] = sum(indicators.values())
    indicators['validated'] = indicators['total_score'] >= 2
    
    return indicators

