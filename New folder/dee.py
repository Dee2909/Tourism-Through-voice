import requests
import pyttsx3
import geocoder
import speech_recognition as sr

def speak(text):
    """Convert text to speech."""
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

def get_speech_input(prompt):
    """Get speech input from the user with retries."""
    r = sr.Recognizer()
    for _ in range(3):  # Try 3 times
        with sr.Microphone() as source:
            speak(prompt)
            audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that. Please repeat.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""
    return ""

def get_latlng(query):
    """Get latitude and longitude from a query."""
    url = "https://api.opencagedata.com/geocode/v1/json"
    apikey = "3e266aa1d068475bb3496b03c5bfe890"
    params = {
        "key": apikey,
        "q": query,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            lat = data["results"][0]["geometry"]["lat"]
            lng = data["results"][0]["geometry"]["lng"]
            return lat, lng
    print(f"Error: {response.status_code}")
    return None, None

def get_top_places(lat, lng):
    """Get top places near a location."""
    url = "https://api.opentripmap.com/0.1/en/places/radius"
    apikey = "5ae2e3f221c38a28845f05b60918257466cd745bcf786b142bfd6528"
    radius = 5000  # 5 km
    limit = 10
    params = {
        "apikey": apikey,
        "radius": radius,
        "lon": lng,
        "lat": lat,
        "limit": limit,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        places = []
        for place in data["features"]:
            name = place["properties"]["name"]
            description = place["properties"].get("wikipedia_extracts", {}).get("text", "")
            places.append(f"{name}: {description}")
        return places
    else:
        print(f"Error: {response.status_code}")
        return []

# Start of the main interaction
greeting = "Hi!"
speak(greeting)

# Destination place
destination = get_speech_input("Tell me your destination place") + ", Tamil Nadu, India"
lat, lng = get_latlng(destination)

if lat is not None and lng is not None:
    speak(f"Famous places in {destination}")
    places = get_top_places(lat, lng)
    if places:
        for idx, place in enumerate(places, start=1):
            print(f"{idx}. {place}")
            speak(f"{idx}. {place.split(':')[0]}")  # Speak only the name of the place

        place_choices = " ".join(f"{idx}" for idx in range(1, len(places) + 1))
        choice = get_speech_input(f"Please choose a number from the list: {place_choices}")

        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(places):
                chosen_place = places[choice_index]
                speak(f"You chose {chosen_place}")
            else:
                speak("Invalid choice.")
        except ValueError:
            speak("Invalid input. Please provide a number.")
    else:
        speak("No famous places found.")
else:
    speak("Sorry, I couldn't find that location.")

# Assuming this next part of code is for starting location:
speak("Tell me your starting place. Say 'current location' or the name of the place.")
starting_place = get_speech_input("From your current location or some other location?")

if starting_place.lower() == "current location":
    location = geocoder.ip('me')
    if location.ok:
        start_lat, start_lng = location.latlng
        print(f"Current Location: {start_lat}, {start_lng}")
        speak(f"Your current location is {location.address}")
    else:
        speak("Unable to get current location.")
else:
    start_location = get_speech_input("Tell me your starting place")
    start_lat, start_lng = get_latlng(start_location)

if start_lat and start_lng:
    print(f"Start: {start_lat}, {start_lng}")
    print(f"Destination: {lat}, {lng}")
else:
    speak("Unable to determine starting location.")
