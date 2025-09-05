# MGVRP Discord Bot

A comprehensive Discord bot for Mellow's Greenville Roleplay server with advanced features including vehicle registration, session management, economy system, moderation tools, and an admin portal.

## Features

### 🚗 Vehicle System
- **Enhanced Vehicle Registration**: Register vehicles with make, model, color, state, and license plate
- **Advanced Search**: Search vehicles by multiple criteria with pagination
- **Vehicle Statistics**: Comprehensive statistics and analytics
- **Transfer System**: Admin-controlled vehicle ownership transfers
- **Personal Fleet**: View all your registered vehicles

### 🎮 Session Management
- **Session Creation**: Create and manage roleplay sessions
- **Participant Tracking**: Track who joins/leaves sessions
- **Status Updates**: Real-time session status management
- **Session Statistics**: Analytics for session hosts and admins

### 💰 Economy System
- **Wallet & Bank**: Separate wallet and bank accounts
- **Daily/Weekly Rewards**: Claim rewards with streak bonuses
- **Work System**: Earn money through various jobs
- **Payment System**: Transfer money between users
- **Leaderboards**: See who's the richest in the server

### 🛡️ Moderation System
- **Warning System**: Issue and track user warnings
- **Timeout Management**: Timeout users with custom durations
- **Kick/Ban System**: Moderation actions with logging
- **Moderation Logs**: All actions are logged automatically

### 🛠️ Admin Portal
- **Server Management**: Channel cleanup, role management, server stats
- **User Management**: Bulk actions, user lookup, inactive member detection
- **Data Management**: Database management, backups, cleanup tools
- **Bot Settings**: Command reloading, system information

### 📊 Additional Features
- **Insurance Claims**: File and track vehicle insurance claims
- **Department Applications**: Pass/fail announcements for department applications
- **Custom Embeds**: Create custom embeds with various styling options
- **Roblox Integration**: Link Discord accounts with Roblox profiles
- **Sticky Messages**: Automatic sticky message management

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mgvrp-discord-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```env
TOKEN=your_discord_bot_token
GUILD_ID=your_guild_id
CLIENT_ID=your_bot_client_id

# Channel IDs
EARLY_ACCESS_CHANNEL=channel_id
SETTING_UP_CHANNEL=channel_id
CONCLUSION_CHANNEL=channel_id
LOG_CHANNEL=channel_id
ECONOMY_CHANNEL=channel_id
MOD_LOG_CHANNEL=channel_id
VEHICLE_REGISTRY_CHANNEL=channel_id
INSURANCE_CHANNEL=channel_id
```

4. Run the bot:
```bash
python bot.py
```

## Commands

### Vehicle System
- `/registervehicle` - Register a new vehicle
- `/lookuplate` - Look up vehicles by license plate
- `/vehicle_search` - Advanced vehicle search with filters
- `/vehicle_stats` - View vehicle database statistics
- `/my_vehicles` - View your registered vehicles
- `/transfer_vehicle` - Transfer vehicle ownership (Admin only)

### Economy System
- `/balance` - Check your or someone's balance
- `/daily` - Claim daily reward
- `/weekly` - Claim weekly reward
- `/work` - Work to earn money
- `/deposit` - Deposit money to bank
- `/withdraw` - Withdraw money from bank
- `/pay` - Pay money to another user
- `/leaderboard` - View economy leaderboard

### Session Management
- `/create_session` - Create a new roleplay session
- `/update_session` - Update session status
- `/active_sessions` - View all active sessions
- `/session_stats` - View session statistics (Staff only)

### Moderation
- `/warn` - Warn a user
- `/warnings` - View user warnings
- `/timeout` - Timeout a user
- `/untimeout` - Remove timeout from user
- `/kick` - Kick a user
- `/ban` - Ban a user

### Admin Portal
- `/admin` - Open the comprehensive admin portal
- `/emergency_shutdown` - Emergency bot shutdown (Admin only)

### Other Commands
- `/ping` - Check bot latency
- `/botstats` - View bot statistics
- `/customembed` - Create custom embeds
- `/insuranceclaim` - File an insurance claim
- `/deptpass` / `/deptfail` - Department application results

## File Structure

```
├── bot.py                          # Main bot file
├── commands/                       # Command modules
│   ├── admin_portal.py            # Comprehensive admin portal
│   ├── enhanced_vehicle_system.py # Advanced vehicle management
│   ├── economy_system.py          # Complete economy system
│   ├── moderation_system.py       # Moderation tools
│   ├── enhanced_session_management.py # Session management
│   └── [other command files]
├── data/                          # Data storage
│   ├── vehicles.json             # Vehicle database
│   ├── economy.json              # Economy data
│   ├── warnings.json             # Warning records
│   └── sessions.json             # Session data
├── utils/                         # Utility functions
│   └── embed.py                  # Embed helpers
├── config.py                     # Configuration
└── requirements.txt              # Dependencies
```

## Configuration

The bot uses environment variables for configuration. Key settings include:

- **TOKEN**: Your Discord bot token
- **GUILD_ID**: Your Discord server ID
- **Channel IDs**: Various channel IDs for different features
- **Role IDs**: Admin and moderator role IDs

## Data Management

The bot automatically creates and manages JSON files for data storage:

- `vehicles.json` - Vehicle registration data
- `economy.json` - User economy data
- `warnings.json` - Moderation warnings
- `sessions.json` - Session management data

Regular backups are recommended and can be created through the admin portal.

## Logging

The bot includes comprehensive logging:

- Console output for real-time monitoring
- File logging to `bot.log`
- Error tracking and reporting
- Moderation action logging

## Support

For support, feature requests, or bug reports, please contact the development team or create an issue in the repository.

## License

This project is proprietary software for Mellow's Greenville Roleplay. Unauthorized distribution or modification is prohibited.