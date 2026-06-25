const users_charts_btn = document.getElementById("users-charts-btn");
const tickets_charts_btn = document.getElementById("tickets-charts-btn");
const it_experts_charts_btn = document.getElementById("it-experts-charts-btn");
const users_charts = document.getElementById("users-charts");
const tickets_charts = document.getElementById("tickets-charts");
const it_experts_charts = document.getElementById("it-experts-charts");

tickets_charts.style.display = "none";
it_experts_charts.style.display = "none";

users_charts_btn.addEventListener("click", async (e) => {
    users_charts_btn.classList.add("stats-active");
    tickets_charts_btn.classList.remove("stats-active");
    it_experts_charts_btn.classList.remove("stats-active");
    users_charts.style.display = "block";
    tickets_charts.style.display = "none";
    it_experts_charts.style.display = "none";
});
tickets_charts_btn.addEventListener("click", async (e) => {
    tickets_charts_btn.classList.add("stats-active");
    users_charts_btn.classList.remove("stats-active");
    it_experts_charts_btn.classList.remove("stats-active");
    tickets_charts.style.display = "block";
    users_charts.style.display = "none";
    it_experts_charts.style.display = "none";
});
it_experts_charts_btn.addEventListener("click", async (e) => {
    it_experts_charts_btn.classList.add("stats-active");
    users_charts_btn.classList.remove("stats-active");
    tickets_charts_btn.classList.remove("stats-active");
    it_experts_charts.style.display = "block";
    users_charts.style.display = "none";
    tickets_charts.style.display = "none";
});
