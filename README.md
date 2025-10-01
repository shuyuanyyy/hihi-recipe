# HiHi Recipe 

![CI/CD](https://github.com/shuyuanyyy/hihi-recipe/actions/workflows/cicd.yaml/badge.svg)

---

## Team Members ✏️
- **Shuyuan Yang**: [shuyuanyyy](https://github.com/shuyuanyyy)
- **Jasmine Zhang**: [Jasminezhang666666](https://github.com/Jasminezhang666666)
- **Yifan Zhang**: [YifanZZZZZZ](https://github.com/YifanZZZZZZ)

---

## Project Overview 📝

Hihi Recipe empowers users to take control of their health and eating habits by offering personalized recipe recommendations based on their preferences and dietary needs. It intelligently filters recipes by time, nutrition, and cuisine, helping users make smarter meal choices. Our goal is to encourage users to discover meals that truly match their lifestyle.

---

## Docker Images 🐳

Web Application: [hihi_recipe web-app docker image](https://hub.docker.com/r/yz9910/web_app)

Database: [hihi_recipe database docker image](https://hub.docker.com/r/yz9910/mongo)


## Application Deployment 🔗
The application is deployed and accessible at: [https://recipe-search-app-8umjs.ondigitalocean.app/login](https://recipe-search-app-8umjs.ondigitalocean.app/login)

## Application in Docker ⚙️
1. Clone the repository
2. Nevigate into the project folder
```
cd 5-final-hihi
```
3. Build the Docker containers
```
docker-compose build
```
4. Start the Application
```
docker-compose up
```
5. Open your browser
```
http://127.0.0.1:5001
```

---

## References 📎
The recipe dataset is from Kaggle [Food.com Recipes and Interactions](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions/data), which is a dataset consisting of 180K+ recipes data crawled from Food.com (GeniusKitchen) online recipe aggregator. 
