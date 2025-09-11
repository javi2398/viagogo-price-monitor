from discord_webhook import DiscordWebhook, DiscordEmbed

def notification_viagogo(
    webhook_url: str,
    event_url: str,
    event_name: str,
    seat_info: str,
    image_url: str,
    price: str,
    checkout_url: str
):
    webhook = DiscordWebhook(url=webhook_url)

    embed = DiscordEmbed(title=event_name, description=event_url, color="12a14b")

    webhook.add_embed(embed)

    embed.add_embed_field(name="Checkout URL", value=checkout_url)
    embed.add_embed_field(name="Ticket info:", value=seat_info)
    embed.add_embed_field(name="Precio", value=price)

    embed.set_image(url=image_url)

    response = webhook.execute()

    if response.status_code == 200:
        print("Detalles de la entrada enviados a Discord")
    else:
        print(f"Error al enviar el webhook, error: {response}")
