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
        
        # Riddles
        self.riddles = [
            {
                "riddle": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
                "answer": "An echo"
            },
            {
                "riddle": "What has hands but cannot clap?",
                "answer": "A clock"
            },
            {
                "riddle": "I am not alive, but I grow. I don't have lungs, but I need air. What am I?",
                "answer": "Fire"
            },
            {
                "riddle": "What gets wet while drying?",
                "answer": "A towel"
            },
            {
                "riddle": "I have cities, but no houses. I have forests, but no trees. I have water, but no fish. What am I?",
                "answer": "A map"
            },
            {
                "riddle": "What can run but never walks, has a mouth but never talks, has a bed but never sleeps?",
                "answer": "A river"
            },
            {
                "riddle": "I have a face and two hands, but no arms or legs. What am I?",
                "answer": "A clock"
            },
            {
                "riddle": "What is full of keys but cannot open any door?",
                "answer": "A piano"
            }
        ]
        
        # Meme captions/templates
        self.memes = [
            "Drake: 👎 That thing | 👍 This thing",
            "Distracted Boyfriend: Looking at phone while girlfriend disapproves",
            "Two Button Panel: Sweating guy choosing between two buttons",
            "Impact Font: THAT'S WHERE YOU'RE WRONG, KIDDO",
            "Woman Yelling at Cat: Woman yelling at confused cat",
            "Expanding Brain: Increasing levels of brilliance",
            "Surprised Pikachu: Surprised face with yellow cheeks",
            "Is This?: Poor quality image of person asking 'Is this X?'",
            "Loss: Four panel comic meme",
            "Stonks: Guy with finger on head saying 'stonks'",
            "This Is Fine: Dog in burning room saying it's fine",
            "Big Brain Time: Person with expanding brain diagram"
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
    
    @commands.hybrid_command(name="riddle", description="Get a random riddle")
    async def riddle(self, ctx):
        """Get a random riddle to solve."""
        riddle_data = random.choice(self.riddles)
        
        embed = discord.Embed(
            title="Riddle 🧩",
            description=riddle_data['riddle'],
            color=0xffa500
        )
        embed.set_footer(text="Type !answer <your_answer> to solve the riddle")
        
        # Store the current riddle for this user
        if not hasattr(self, 'current_riddles'):
            self.current_riddles = {}
        self.current_riddles[ctx.author.id] = riddle_data['answer'].lower()
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="answer", description="Answer the current riddle")
    async def answer_riddle(self, ctx, *, answer: str):
        """Submit an answer to the riddle."""
        if not hasattr(self, 'current_riddles') or ctx.author.id not in self.current_riddles:
            await ctx.send("No active riddle for you! Use !riddle to get one.")
            return
        
        correct_answer = self.current_riddles[ctx.author.id]
        user_answer = answer.lower().strip()
        
        if user_answer == correct_answer:
            embed = discord.Embed(
                title="Correct! 🎉",
                description=f"Yes! The answer is **{correct_answer}**",
                color=0x00ff00
            )
            # Remove the riddle so they can get another
            del self.current_riddles[ctx.author.id]
        else:
            embed = discord.Embed(
                title="Wrong Answer ❌",
                description=f"That's not quite right. Try again or use !riddle for a new one.",
                color=0xff0000
            )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="meme", description="Get a random meme template")
    async def meme(self, ctx):
        """Get a random meme template."""
        meme = random.choice(self.memes)
        
        embed = discord.Embed(
            title="Meme Template 🎬",
            description=meme,
            color=0xff1493
        )
        embed.set_footer(text="Create memes with these templates!")
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(FunCog(bot))