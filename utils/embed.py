import discord

def create_embed(title: str, description: str, color: int = 0x89CFF0) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="Mellow's Greenville Roleplay™")
    embed.set_thumbnail(url="https://message.style/cdn/images/62c6b688787b4e26c30146c63bd0e1b0fa96f0d6d431e3d3c46ef6497d939cf3.png")
    return embed
