from rMoistPi.client import Client

if __name__ == "__main__":
    client = Client(debug=True)

    from rMoistPi.message import moisture_message

    client.run([moisture_message.MoistureMessage])