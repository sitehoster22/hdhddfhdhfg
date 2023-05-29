import discord
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

client = commands.Bot(command_prefix='/', intents=intents)

# Player data storage
player_data = {}

# Deck of cards
deck = [
    '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A',
    '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A',
    '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A',
    '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'
]

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

    # Register slash commands
    guild_id = 1112022549639999608

    await client.get_guild(guild_id).slash_command('adddeposit', description='Add balance to your account') \
        .option('amount', 'The amount to add', type=int, required=True).register()
    await client.get_guild(guild_id).slash_command('blackjack', description='Start a game of blackjack') \
        .option('bet', 'The amount to bet', type=int, required=True).register()

@client.slash_command()
async def adddeposit(ctx, amount: int):
    user_id = ctx.author.id

    # Check if the user is already registered
    if user_id not in player_data:
        player_data[user_id] = {'balance': 0}

    # Update the player's balance
    player_data[user_id]['balance'] += amount

    response = discord.Embed(
        title='Deposit Added',
        description=f"Successfully added {amount} to your balance.",
        color=discord.Color.green()
    )

    await ctx.send(embed=response)

@client.slash_command()
async def blackjack(ctx, bet: int):
    user_id = ctx.author.id

    # Check if the user is already registered
    if user_id not in player_data:
        response = discord.Embed(
            title='Error',
            description='You need to add a deposit first. Use `/adddeposit <amount>`.',
            color=discord.Color.red()
        )
        return await ctx.send(embed=response)

    player = player_data[user_id]

    # Check if the player has sufficient balance for the bet
    if player['balance'] < bet:
        response = discord.Embed(
            title='Error',
            description='Insufficient balance for the bet.',
            color=discord.Color.red()
        )
        return await ctx.send(embed=response)

    # Deal initial cards
    player_hand = []
    dealer_hand = []

    player_hand.append(draw_card())
    dealer_hand.append(draw_card())
    player_hand.append(draw_card())
    dealer_hand.append(draw_card())

    player_sum = calculate_hand_sum(player_hand)
    dealer_sum = calculate_hand_sum(dealer_hand)

    # Display initial hands
    player_hand_string = get_hand_string(player_hand)
    dealer_hand_string = get_hand_string(dealer_hand[:1])

    response = discord.Embed(
        title='Blackjack',
        color=discord.Color.white()
    )
    response.add_field(name='Your Hand:', value=player_hand_string, inline=False)
    response.add_field(name="Dealer's Hand:", value=dealer_hand_string, inline=False)

    message = await ctx.send(embed=response)

    # Game logic
    game_ended = False

    while not game_ended:
        # Player's turn
        player_action_row = discord.ui.MessageActionRow(
            discord.ui.Button(style=discord.ButtonStyle.primary, label='Hit', custom_id='hit'),
            discord.ui.Button(style=discord.ButtonStyle.primary, label='Stand', custom_id='stand')
        )

        player_turn_response = await ctx.send('Choose your action:', components=[player_action_row])

        try:
            player_turn_interaction = await client.wait_for(
                'button_click',
                check=lambda i: i.user.id == user_id and i.component.custom_id in ['hit', 'stand'],
                timeout=10
            )
        except asyncio.TimeoutError:
            # Handle timeout for player's turn
            timeout_response = discord.Embed(
                title='Timeout',
                description='Your turn has timed out.',
                color=discord.Color.red()
            )
            return await ctx.send(embed=timeout_response)

        if player_turn_interaction.component.custom_id == 'hit':
            new_card = draw_card()
            player_hand.append(new_card)
            new_sum = calculate_hand_sum(player_hand)

            if new_sum > 21:
                game_ended = True
                # Player busted
                # ...

            else:
                updated_player_hand_string = get_hand_string(player_hand)
                updated_response = discord.Embed(
                    title='Blackjack',
                    color=discord.Color.white()
                )
                updated_response.add_field(name='Your Hand:', value=updated_player_hand_string, inline=False)
                updated_response.add_field(name="Dealer's Hand:", value=dealer_hand_string, inline=False)

                await player_turn_interaction.message.edit(embed=updated_response, components=[])

        elif player_turn_interaction.component.custom_id == 'stand':
            game_ended = True

        # ...

def draw_card():
    random_index = random.randint(0, len(deck) - 1)
    return deck.pop(random_index)

def calculate_hand_sum(hand):
    sum = 0
    num_aces = 0

    for card in hand:
        if card == 'A':
            sum += 11
            num_aces += 1
        elif card in ['K', 'Q', 'J']:
            sum += 10
        else:
            sum += int(card)

    while sum > 21 and num_aces > 0:
        sum -= 10
        num_aces -= 1

    return sum

def get_hand_string(hand):
    return ', '.join(hand)

client.run('MTExMjAyMjY3NzgyNjMxODQxNg.GpDnlV.iJTXoA3cNgs7mfGO8JyzOYpDTVLDE2RN9WkkTs')
