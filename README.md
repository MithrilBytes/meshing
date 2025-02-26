# Real-Time Satellite Mesh Network

Ever wondered what’s flying above your head right now?  
This project visualizes real-time satellites orbiting the Earth and connects them in a mesh network based on their proximity. Think of it as a cosmic game of "Tag," except the players are speeding around the planet at 28,000 km/h.

With this, you can:
- Watch satellites orbit the Earth in real-time.
- See mesh connections between satellites within range.
- Feel like a space overlord without leaving your chair.

---

## How Does It Work?

1. **TLE Data:** It pulls real-time Two-Line Element (TLE) data from [CelesTrak](https://celestrak.org/), which is like a GPS for satellites.  
2. **Orbit Calculation:** Using the `skyfield` library, it calculates each satellite's position.  
3. **Mesh Magic:** If two satellites are within 1500 km of each other, they form a "friendship bracelet" (a blue line).  
4. **Dash & Plotly:** The visualization refreshes every 10 seconds, without opening 100 browser tabs like a chaotic robot.

---

<img width="1711" alt="Screenshot 2025-02-25 at 7 35 22 PM" src="https://github.com/user-attachments/assets/7e01dd7a-1cfa-4337-80e9-f2f22f3eade3" />
