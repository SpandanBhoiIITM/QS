from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)


menu = {
    "1": {"item": "Paneer Roll", "price": 60},
    "2": {"item": "Veg Burger", "price": 50},
    "3": {"item": "Cold Coffee", "price": 40}
}

user_state = {}

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip().lower()
    from_number = request.values.get("From", "")
    response = MessagingResponse()
    msg = response.message()

    if from_number not in user_state:
        user_state[from_number] = {"step": "menu"}
        menu_text = "🍽️ *Welcome to QuickServe!*\nChoose an item:\n"
        for k, v in menu.items():
            menu_text += f"{k}. {v['item']} - ₹{v['price']}\n"
        menu_text += "\n_Reply with item number (e.g., 1)_"
        msg.body(menu_text)
        return str(response)

    state = user_state[from_number]

    if state["step"] == "menu":
        if incoming_msg in menu:
            state["item"] = menu[incoming_msg]["item"]
            state["price"] = menu[incoming_msg]["price"]
            state["step"] = "quantity"
            msg.body(f"How many *{state['item']}* do you want?")
        else:
            msg.body("Please choose a valid item number from the menu.")
        return str(response)

    if state["step"] == "quantity":
        if incoming_msg.isdigit():
            state["quantity"] = int(incoming_msg)
            state["step"] = "address"
            msg.body("📍 Please enter your delivery address or hostel/room:")
        else:
            msg.body("Please enter a valid number for quantity.")
        return str(response)

    if state["step"] == "address":
        state["address"] = incoming_msg
        total = state["price"] * state["quantity"]
        msg.body(
            f"✅ *Order Summary:*\n"
            f"{state['quantity']} x {state['item']} = ₹{total}\n"
            f"📍 Delivery at: {state['address']}\n\n"
            "Thank you for ordering with QuickServe! 🛵🍴"
        )
        del user_state[from_number]
        return str(response)

    msg.body("Something went wrong. Let's start again.")
    user_state.pop(from_number, None)
    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port, debug=True)
