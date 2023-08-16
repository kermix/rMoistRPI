from rMoistPi import client

from rMoistPi.message import moisture_message

if __name__ == "__main__":
    c = client.Client()
    c.run([moisture_message.MoistureMessage])