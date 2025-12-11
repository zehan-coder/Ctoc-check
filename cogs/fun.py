"""
Fun Commands for Discord Bot
Provides entertaining commands like jokes, 8ball, random responses, etc.
"""

import random
from typing import Optional

import discord
from discord.ext import commands


class FunCog(commands.Cog):
    """Fun and entertainment commands."""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Jokes list
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it was full of problems!",
            "What do you call a sleeping bull? A bulldozer!",
            "Why don't skeletons fight each other? They don't have the guts!",
            "What's orange and sounds like a parrot? A carrot!",
            "Why did the cookie go to the doctor? Because it felt crumbly!",
            "What do you call a bear with no teeth? A gummy bear!"
        ]
        
        # 8ball responses
        self.eight_ball_responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.",
            "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.",
            "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
            "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]
    
    @commands.hybrid_command(name="joke", description="Tell a random joke")
    async def joke(self, ctx):
        """Tell a random joke."""
        joke = random.choice(self.jokes)
        
        embed = discord.Embed(
            title="Here's a joke!",
            description=joke,
            color=0xffd700
        )
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="8ball", description="Ask the magic 8ball a question")
    async def eight_ball(self, ctx, *, question: str):
        """Ask the magic 8ball a question."""
        if not question:
            await ctx.send("Please ask a question!")
            return
        
        response = random.choice(self.eight_ball_responses)
        
        # Determine embed color based on response
        if response in ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", 
                       "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", 
                       "Yes.", "Signs point to yes."]:
            color = 0x00ff00  # Green for positive
        elif response in ["Reply hazy, try again.", "Ask again later.", "Better not tell you now.", 
                         "Cannot predict now.", "Concentrate and ask again."]:
            color = 0xffff00  # Yellow for neutral
        else:
            color = 0xff0000  # Red for negative
        
        embed = discord.Embed(
            title="Magic 8ball",
            color=color
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=f"**{response}**", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="coinflip", description="Flip a coin")
    async def coinflip(self, ctx):
        """Flip a coin."""
        result = random.choice(["Heads", "Tails"])
        
        embed = discord.Embed(
            title="Coin Flip",
            description=f"**Result:** {result}!",
            color=0x00ffff
        )
        embed.set_footer(text=f"The coin landed on {result.lower()}")
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(FunCog(bot))