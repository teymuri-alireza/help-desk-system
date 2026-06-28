const data_user_role = document.getElementById("user-role-data");
const users_charts_btn = document.getElementById("users-charts-btn");
const tickets_charts_btn = document.getElementById("tickets-charts-btn");
const it_experts_charts_btn = document.getElementById("it-experts-charts-btn");
const users_charts = document.getElementById("users-charts");
const tickets_charts = document.getElementById("tickets-charts");
const it_experts_charts = document.getElementById("it-experts-charts");

const user_role = data_user_role.dataset.user_role;

if (user_role == "System Admin") {

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
} 

else {
    users_charts_btn.remove()

    tickets_charts_btn.classList.add("stats-active");
    it_experts_charts.style.display = "none";

    tickets_charts_btn.addEventListener("click", async (e) => {
        tickets_charts_btn.classList.add("stats-active");
        it_experts_charts_btn.classList.remove("stats-active");
        tickets_charts.style.display = "block";
        it_experts_charts.style.display = "none";
    });
    it_experts_charts_btn.addEventListener("click", async (e) => {
        it_experts_charts_btn.classList.add("stats-active");
        tickets_charts_btn.classList.remove("stats-active");
        it_experts_charts.style.display = "block";
        tickets_charts.style.display = "none";
    });
}