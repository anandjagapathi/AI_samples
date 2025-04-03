import random
import os
import requests  # Make sure to import requests
from dotenv import load_dotenv
from llama_index.utils.workflow import draw_all_possible_flows
from llama_index.utils.workflow import draw_most_recent_execution
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Context
)

# Load environment variables from .env file
load_dotenv()
openai_api_key = os.environ["OPENAI_API_KEY"]
weather_api_key = os.getenv("OPENWEATHERMAP_API_KEY")


class CityEvent(Event):
    city: str


class WeFlow(Workflow):
    llm = OpenAI(model="gpt-4o-mini", api_key=openai_api_key)

    @step
    async def generate_city(self, ev: StartEvent) -> CityEvent:
        topic = ev.topic
        prompt = f"Extract only city name {topic}."
        response = await self.llm.acomplete(prompt)
        city_name = str(response)
        return CityEvent(city=city_name)

    @step
    async def generate_weather(self, ev: CityEvent) -> StopEvent:
        city = ev.city  # Correctly access the city from the event
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        weather_info = f"The weather in {city} is {weather_description} with a temperature of {temperature}°C."
# #
#         if data["cod"] == 200:
#             weather_description = data['weather'][0]['description']
#             temperature = data['main']['temp']
#             weather_info = f"The weather in {city} is {weather_description} with a temperature of {temperature}°C."
#         else:
#             weather_info = f"Could not get weather for {city}."

        return StopEvent(result=weather_info)  # Return the weather info as the final result




# Main async function to run the workflow
async def main():
    w = WeFlow(timeout=60, verbose=False)
    result = await w.run(topic="Weather in newyork")
    print(f"Workflow result: {result}")  # Print the final result


# Call the main function to execute the workflow
import asyncio
asyncio.run(main())