# Custom Integration for DeWarmte Heat pumps

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

This s a custom integration for [Home Assistant](https://www.home-assistant.io) that connects to the **DeWarmte** API to fetch and display sensor data from your heat pump device.

*Tested with single heat pump device in hybrid setup.*

---

## 🔧 Features

- Authentication via email & password
- Token refresh management (access + refresh tokens)
- Automatically retrieves device status
- Adds sensor entities for:
  - Supply Temperature
  - Target Temperature
  - Actual Temperature
  - Heat Output / Input
  - Water flow
  - On/Off State
  - Connection Status
  - Outside Temperature
  - COP
  - Consumed electricity from insights endpoint
  - Sum of electricity consumption from hourly windows of insights endpoint

---

## 📦 Installation

1. via HACS - _preferred way_
1. Navigate to your Home Assistant `config/custom_components/` directory:
   ```bash
   mkdir -p custom_components/my_integration

