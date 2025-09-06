#!/usr/bin/env python3
"""
MGVRP Bot Web Management Server
Provides a web interface for managing the Discord bot with real data integration
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import discord
from discord.ext import commands
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = Path("data")
WEB_DIR = Path("web")
GUILD_ID = int(os.getenv("GUILD_ID", "1277047315047120978"))

app = Flask(__name__, static_folder='web', template_folder='web')
CORS(app)

# Bot reference (will be set when bot starts)
bot_instance = None

class WebManager:
    def __init__(self, bot):
        self.bot = bot
        global bot_instance
        bot_instance = bot
    
    def load_json_file(self, filename: str) -> Dict[str, Any]:
        """Load data from JSON file"""
        file_path = DATA_DIR / filename
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"File {filename} not found, returning empty data")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing {filename}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return {}
    
    def save_json_file(self, filename: str, data: Dict[str, Any]) -> bool:
        """Save data to JSON file"""
        file_path = DATA_DIR / filename
        try:
            DATA_DIR.mkdir(exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
            return False
    
    def get_bot_stats(self) -> Dict[str, Any]:
        """Get comprehensive bot statistics from real data"""
        try:
            # Vehicle stats
            vehicles_data = self.load_json_file("vehicles.json")
            total_vehicles = len(vehicles_data.get('vehicles', []))
            
            # Economy stats
            economy_data = self.load_json_file("economy.json")
            total_users = len(economy_data.get('users', {}))
            
            # Session stats
            sessions_data = self.load_json_file("sessions.json")
            sessions = sessions_data.get('sessions', [])
            active_sessions = len([s for s in sessions if s.get('status') != 'Ended'])
            
            # Warning stats
            warnings_data = self.load_json_file("warnings.json")
            total_warnings = len(warnings_data.get('data', []))
            
            # System stats
            import psutil
            memory_usage = f"{psutil.virtual_memory().percent:.1f}%"
            cpu_usage = f"{psutil.cpu_percent(interval=1):.1f}%"
            
            # Bot uptime
            if hasattr(self.bot, 'start_time'):
                uptime_delta = datetime.utcnow() - self.bot.start_time
                days = uptime_delta.days
                hours, remainder = divmod(uptime_delta.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                uptime = f"{days}d {hours}h {minutes}m"
            else:
                uptime = "Unknown"
            
            return {
                'totalVehicles': total_vehicles,
                'totalUsers': total_users,
                'activeSessions': active_sessions,
                'totalWarnings': total_warnings,
                'memoryUsage': memory_usage,
                'cpuUsage': cpu_usage,
                'uptime': uptime,
                'botStatus': 'online' if self.bot.is_ready() else 'offline',
                'guildCount': len(self.bot.guilds) if self.bot.guilds else 0,
                'memberCount': sum(guild.member_count for guild in self.bot.guilds) if self.bot.guilds else 0
            }
        except Exception as e:
            logger.error(f"Error getting bot stats: {e}")
            return {
                'totalVehicles': 0,
                'totalUsers': 0,
                'activeSessions': 0,
                'totalWarnings': 0,
                'memoryUsage': 'N/A',
                'cpuUsage': 'N/A',
                'uptime': 'N/A',
                'botStatus': 'offline',
                'guildCount': 0,
                'memberCount': 0
            }

# Initialize web manager
web_manager = None

# Routes
@app.route('/')
def index():
    """Serve the main web interface"""
    return send_from_directory('web', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('web', filename)

@app.route('/api/stats')
def get_stats():
    """Get bot statistics from real data"""
    if web_manager:
        return jsonify(web_manager.get_bot_stats())
    return jsonify({'error': 'Bot not connected'}), 503

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    """Get all vehicles from real data"""
    try:
        if not web_manager:
            return jsonify({'error': 'Bot not connected'}), 503
        
        vehicles_data = web_manager.load_json_file("vehicles.json")
        vehicles = vehicles_data.get('vehicles', [])
        
        # Add owner usernames if bot is available
        if bot_instance:
            guild = bot_instance.get_guild(GUILD_ID)
            if guild:
                for vehicle in vehicles:
                    user_id = vehicle.get('userId')
                    if user_id:
                        try:
                            member = guild.get_member(int(user_id))
                            vehicle['ownerName'] = member.display_name if member else f"User#{user_id}"
                            vehicle['ownerAvatar'] = str(member.avatar.url) if member and member.avatar else None
                        except:
                            vehicle['ownerName'] = f"User#{user_id}"
                            vehicle['ownerAvatar'] = None
        
        return jsonify(vehicles)
    except Exception as e:
        logger.error(f"Error getting vehicles: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    """Add a new vehicle to real data"""
    try:
        if not web_manager:
            return jsonify({'error': 'Bot not connected'}), 503
        
        data = request.json
        vehicles_data = web_manager.load_json_file("vehicles.json")
        
        if 'vehicles' not in vehicles_data:
            vehicles_data['vehicles'] = []
        
        # Check for duplicate plate in same state
        existing = any(
            v['plate'].upper() == data['plate'].upper() and 
            v['state'].upper() == data['state'].upper() 
            for v in vehicles_data['vehicles']
        )
        
        if existing:
            return jsonify({'error': 'Vehicle with this plate already exists in this state'}), 400
        
        # Create new vehicle
        new_vehicle = {
            'userId': data['owner'],
            'make': data['make'].strip().title(),
            'model': data['model'].strip().title(),
            'color': data['color'].strip().title(),
            'state': data['state'].upper(),
            'plate': data['plate'].upper(),
            'registeredAt': datetime.utcnow().isoformat() + 'Z'
        }
        
        vehicles_data['vehicles'].append(new_vehicle)
        
        if web_manager.save_json_file("vehicles.json", vehicles_data):
            return jsonify({'success': True, 'vehicle': new_vehicle})
        else:
            return jsonify({'error': 'Failed to save vehicle data'}), 500
            
    except Exception as e:
        logger.error(f"Error adding vehicle: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/vehicles/<int:vehicle_index>', methods=['DELETE'])
def delete_vehicle(vehicle_index):
    """Delete a vehicle from real data"""
    try:
        if not web_manager:
            return jsonify({'error': 'Bot not connected'}), 503
        
        vehicles_data = web_manager.load_json_file("vehicles.json")
        vehicles = vehicles_data.get('vehicles', [])
        
        if 0 <= vehicle_index < len(vehicles):
            deleted_vehicle = vehicles.pop(vehicle_index)
            
            if web_manager.save_json_file("vehicles.json", vehicles_data):
                return jsonify({'success': True, 'deleted': deleted_vehicle})
            else:
                return jsonify({'error': 'Failed to save changes'}), 500
        else:
            return jsonify({'error': 'Vehicle not found'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting vehicle: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/economy', methods=['GET'])
def get_economy():
    """Get economy data from real data"""
    try:
        if not web_manager:
            return jsonify({'error': 'Bot not connected'}), 503
        
        economy_data = web_manager.load_json_file("economy.json")
        users_data = economy_data.get('users', {})
        
        users = []
        total_money = 0
        
        for user_id, user_data in users_data.items():
            balance = user_data.get('balance', 0)
            bank = user_data.get('bank', 0)
            total_wealth = balance + bank
            total_money += total_wealth
            
            # Get username if bot is available
            username = f"User#{user_id}"
            avatar = None
            
            if bot_instance:
                guild = bot_instance.get_guild(GUILD_ID)
                if guild:
                    try:
                        member = guild.get_member(int(user_id))
                        if member:
                            username = member.display_name
                            avatar = str(member.avatar.url) if member.avatar else None
                    except:
                        pass
            
            users.append({
                'id': user_id,
                'username': username,
                'avatar': avatar,
                'balance': balance,
                'bank': bank,
                'total': total_wealth,
                'totalEarned': user_data.get('total_earned', 0),
                'totalSpent': user_data.get('total_spent', 0),
                'lastDaily': user_data.get('last_daily'),
                'lastWeekly': user_data.get('last_weekly'),
                'lastWork': user_data.get('last_work')
            })
        
        # Sort by total wealth
        users.sort(key=lambda x: x['total'], reverse=True)
        
        return jsonify({
            'users': users,
            'totalMoney': total_money,
            'averageWealth': total_money / len(users) if users else 0,
            'richestUser': users[0]['username'] if users else 'None'
        })
        
    except Exception as e:
        logger.error(f"Error getting economy data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get sessions from real data"""
    try:
        if not web_manager:
            return jsonify({'error': 'Bot not connected'}), 503
        
        sessions_data = web_manager.load_json_file("sessions.json")
        sessions = sessions_data.get('sessions', [])
        
        # Add host usernames if bot is available
        if bot_instance:
            guild = bot_instance.get_guild(GUILD_ID)
            if guild:
                for session in sessions:
                    host_id = session.get('host_id')
                    if host_id:
                        try:
                            member = guild.get_member(int(host_id))
                            session['hostName'] = member.display_name if member else f"User#{host_id}"
                            session['hostAvatar'] = str(member.avatar.url) if member and member.avatar else None
                        except:
                            session['hostName'] = f"User#{host_id}"
                            session['hostAvatar'] = None
                    
                    cohost_id = session.get('cohost_id')
                    if cohost_id:
                        try:
                            member = guild.get_member(int(cohost_id))
                            session['cohostName'] = member.display_name if member else f"User#{cohost_id}"
                        except:
                            session['cohostName'] = f"User#{cohost_id}"
        
        return jsonify(sessions)
        
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/moderation', methods=['GET'])
def get_moderation():
    """Get moderation data from real data"""
    try:
        if not web_manager:
            return jsonify({'error': 'Bot not connected'}), 503
        
        warnings_data = web_manager.load_json_file("warnings.json")
        warnings = warnings_data.get('data', [])
        
        # Process warnings data
        processed_warnings = []
        for warning in warnings[-50:]:  # Last 50 warnings
            user_id = warning.get('user_id')
            mod_id = warning.get('moderator_id')
            
            user_name = f"User#{user_id}"
            mod_name = f"Mod#{mod_id}"
            user_avatar = None
            
            if bot_instance:
                guild = bot_instance.get_guild(GUILD_ID)
                if guild:
                    try:
                        user = guild.get_member(int(user_id))
                        moderator = guild.get_member(int(mod_id))
                        if user:
                            user_name = user.display_name
                            user_avatar = str(user.avatar.url) if user.avatar else None
                        if moderator:
                            mod_name = moderator.display_name
                    except:
                        pass
            
            processed_warnings.append({
                'id': warning.get('id'),
                'userId': user_id,
                'userName': user_name,
                'userAvatar': user_avatar,
                'moderatorId': mod_id,
                'moderatorName': mod_name,
                'reason': warning.get('reason', 'No reason'),
                'timestamp': warning.get('timestamp'),
                'status': 'Active'
            })
        
        return jsonify({
            'warnings': processed_warnings,
            'totalWarnings': len(warnings),
            'activeTimeouts': 0,  # Would need separate tracking
            'recentBans': 0       # Would need separate tracking
        })
        
    except Exception as e:
        logger.error(f"Error getting moderation data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get guild users"""
    try:
        if not bot_instance:
            return jsonify({'error': 'Bot not connected'}), 503
        
        guild = bot_instance.get_guild(GUILD_ID)
        if not guild:
            return jsonify({'error': 'Guild not found'}), 404
        
        users = []
        for member in guild.members[:100]:  # Limit to first 100 members
            users.append({
                'id': str(member.id),
                'username': member.display_name,
                'discriminator': member.discriminator,
                'avatar': str(member.avatar.url) if member.avatar else str(member.default_avatar.url),
                'joinedAt': member.joined_at.isoformat() if member.joined_at else None,
                'roles': [role.name for role in member.roles if role.name != '@everyone'],
                'status': str(member.status).title(),
                'isBot': member.bot,
                'permissions': {
                    'administrator': member.guild_permissions.administrator,
                    'moderateMembers': member.guild_permissions.moderate_members,
                    'manageMessages': member.guild_permissions.manage_messages
                }
            })
        
        return jsonify(users)
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/economy/action', methods=['POST'])
def economy_action():
    """Perform economy action on real data"""
    try:
        if not web_manager:
            return jsonify({'error': 'Bot not connected'}), 503
        
        data = request.json
        user_id = data['user']
        action = data['action']
        amount = int(data['amount'])
        target = data['target']  # 'balance' or 'bank'
        
        economy_data = web_manager.load_json_file("economy.json")
        
        if 'users' not in economy_data:
            economy_data['users'] = {}
        
        if user_id not in economy_data['users']:
            economy_data['users'][user_id] = {
                'balance': 0,
                'bank': 0,
                'total_earned': 0,
                'total_spent': 0
            }
        
        user_data = economy_data['users'][user_id]
        
        if action == 'add':
            user_data[target] += amount
            user_data['total_earned'] += amount
        elif action == 'remove':
            user_data[target] = max(0, user_data[target] - amount)
            user_data['total_spent'] += amount
        elif action == 'set':
            user_data[target] = amount
        
        if web_manager.save_json_file("economy.json", economy_data):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to save changes'}), 500
            
    except Exception as e:
        logger.error(f"Error performing economy action: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent-activity')
def get_recent_activity():
    """Get recent activity from real data"""
    try:
        if not web_manager:
            return jsonify([])
        
        activities = []
        
        # Recent vehicles
        vehicles_data = web_manager.load_json_file("vehicles.json")
        for vehicle in vehicles_data.get('vehicles', [])[-5:]:
            try:
                reg_time = datetime.fromisoformat(vehicle['registeredAt'].replace('Z', '+00:00'))
                time_ago = datetime.utcnow() - reg_time.replace(tzinfo=None)
                if time_ago.days < 7:
                    activities.append({
                        'icon': 'fas fa-car',
                        'text': f"Vehicle {vehicle['plate']} registered",
                        'time': f"{time_ago.days}d {time_ago.seconds//3600}h ago" if time_ago.days > 0 else f"{time_ago.seconds//60}m ago"
                    })
            except:
                continue
        
        # Recent sessions
        sessions_data = web_manager.load_json_file("sessions.json")
        for session in sessions_data.get('sessions', [])[-3:]:
            try:
                created_time = datetime.fromisoformat(session['created_at'])
                time_ago = datetime.utcnow() - created_time
                if time_ago.days < 7:
                    activities.append({
                        'icon': 'fas fa-gamepad',
                        'text': f"Session #{session['id']} created",
                        'time': f"{time_ago.days}d {time_ago.seconds//3600}h ago" if time_ago.days > 0 else f"{time_ago.seconds//60}m ago"
                    })
            except:
                continue
        
        # Recent warnings
        warnings_data = web_manager.load_json_file("warnings.json")
        for warning in warnings_data.get('data', [])[-3:]:
            try:
                warn_time = datetime.fromisoformat(warning['timestamp'])
                time_ago = datetime.utcnow() - warn_time
                if time_ago.days < 7:
                    activities.append({
                        'icon': 'fas fa-exclamation-triangle',
                        'text': f"Warning issued to user",
                        'time': f"{time_ago.days}d {time_ago.seconds//3600}h ago" if time_ago.days > 0 else f"{time_ago.seconds//60}m ago"
                    })
            except:
                continue
        
        # Sort by most recent and limit
        return jsonify(activities[-10:])
        
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return jsonify([])

def start_web_server(bot, host='0.0.0.0', port=5000):
    """Start the web server"""
    global web_manager
    web_manager = WebManager(bot)
    
    logger.info(f"Starting web server on {host}:{port}")
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    # For testing without bot
    app.run(host='0.0.0.0', port=5000, debug=True)