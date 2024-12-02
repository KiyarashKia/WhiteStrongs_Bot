# WhiteStrongs_Bot

## **Case Study: Real-Time Telegram Bot for Live Football Updates**

### **Objective**
To create a Telegram bot that provides real-time updates for live football matches, specifically tailored for Real Madrid supporters. The bot serves as a co-pilot or assistant for channel admins, ensuring they don't miss any events and can easily keep their audience informed.

The bot should:
- Fetch and display live match events (goals, cards, substitutions, etc.) every 30 seconds.
- Support commands for starting, stopping, and checking live updates.
- Ensure secure and reliable operation with environment management and a status page for monitoring.

---

## **Overview of the Stack**

- **Python:** The primary programming language for building the bot due to its rich library ecosystem.
- **Libraries/Frameworks:**
  - `python-telegram-bot`: For interacting with Telegram's API.
  - `requests`: For making API calls to the football match data provider.
  - `dotenv`: For managing environment variables and securing sensitive data.
  - `nest_asyncio`: To handle nested asynchronous operations in the event loop.
  - `Flask`: For creating a simple status page to monitor bot uptime.
- **Postman:** Used for testing the API endpoints and understanding response structures.
- **UptimeRobot:** Monitors the bot's operational status via the Flask endpoint.
- **Replit:** Used as the deployment platform for seamless hosting and secret management.

---

## **Challenges and Solutions**

### **1. Fetching Live Match Data**
- **Challenge:** Retrieve live match data from the football API and map team names/events to Farsi.
- **Solution:**
  - Used Postman to test the API and understand the response structure.
  - Created a `TEAM_NAMES_FARSI` dictionary for mapping English names to Farsi.
  - Designed a helper function (`fetch_live_fixture`) to retrieve the live match fixture ID for Real Madrid.

### **2. Real-Time Updates**
- **Challenge:** Continuously fetch and send updates every 30 seconds without duplicating events.
- **Solution:**
  - Used `asyncio` for asynchronous operations.
  - Implemented a `send_live_updates` function that runs in a loop and tracks already sent events using a `set`.
  - Added a `/stop` command to gracefully end the update loop.

### **3. Handling Sensitive Data**
- **Challenge:** Protect API keys and bot tokens from being exposed in public repositories.
- **Solution:**
  - Used a `.env` file to store sensitive data and `python-dotenv` to load them securely into the program.
  - Added `.env` to `.gitignore` to exclude it from version control.

### **4. Monitoring Bot Uptime**
- **Challenge:** Ensure the bot is operational and reflect its status on a public status page.
- **Solution:**
  - Used Flask to create a simple HTTP endpoint (`/`) that responds with the bot's operational status.
  - Integrated UptimeRobot to monitor this endpoint and display the status on a public page.

### **5. Deployment on Replit**
- **Challenge:** Set up the bot on Replit and keep it alive.
- **Solution:**
  - Used Replit's secret manager for securely storing API keys and tokens.
  - Configured the Flask app and threading to ensure continuous operation.

---

## **Use Case: Live Football Updates Bot**

### **Primary Users**
- **Channel Admins:** Use the bot as a co-pilot or assistant to ensure no events are missed, reducing their workload and keeping the audience informed.
- **Football Fans:** Receive real-time match updates for their favorite team, Real Madrid, in their preferred language (Farsi).

### **Key Features**
1. **Commands:**
   - `/start`: Introduces the bot and displays available commands.
   - `/live`: Starts sending live updates for Real Madrid's match.
   - `/stop`: Stops sending updates.
2. **Automatic Updates:**
   - The bot fetches live match events (goals, cards, substitutions) every 30 seconds and sends them to the Telegram channel.
   - Custom messages for Real Madrid goals, e.g., “گللللللللللللل برای رئال مادرید!”
3. **Monitoring:**
   - A public status page indicates whether the bot is running and operational.

---

## **Reflection**

### **What Did I Learn?**
1. **APIs and Real-Time Data:**
   - Understanding how to work with RESTful APIs and handle live data.
   - Using tools like Postman to debug and test API responses.
2. **Asynchronous Programming:**
   - Implementing periodic data fetching with `asyncio`.
   - Handling duplicate events using unique identifiers.
3. **Security Best Practices:**
   - Storing sensitive data in `.env` files and securing it with `.gitignore`.
   - Using environment variables for better security in deployment.
4. **Deployment and Monitoring:**
   - Deploying the bot on Replit and integrating Flask for uptime monitoring.
   - Using UptimeRobot to monitor the bot's status and display it on a public page.
5. **Localization:**
   - Translating football events into Farsi for a better user experience.

---

### **What Were My Challenges?**
1. **Asynchronous Design:** Ensuring live updates were non-blocking and operated smoothly without duplication.
2. **Environment Management:** Securing sensitive keys and ensuring compatibility between local development and production.
3. **Debugging API Integration:** Handling cases where live match data was unavailable or delayed.

---

### **How Did I Solve Them?**
- **Research and Learning:** Consulted Python documentation, explored library capabilities, and tested APIs with Postman.
- **Iteration:** Refined the bot’s functionality through trial and error, debugging issues as they arose.
- **Community and Collaboration:** Asked questions, gathered feedback, and adapted best practices.

---

### **Updates**
1. TBD

---
# Bot Status
- https://stats.uptimerobot.com/t2bYCOQ6zV