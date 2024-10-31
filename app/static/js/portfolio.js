document.addEventListener("DOMContentLoaded", function () {
    // 1. INITIALIZATION
    // -----------------
    const portfolioDataElement = document.getElementById("portfolio-data");
    const allStocksDataElement = document.getElementById("all-stocks-data");

    console.log("Raw portfolio data:", portfolioDataElement.getAttribute("data-portfolio"));
    console.log("Raw all stocks data:", allStocksDataElement.getAttribute("data-all-stocks"));

    // Check if data attributes exist and are not empty before parsing
    const portfolioStocks = portfolioDataElement.getAttribute("data-portfolio")
    ? JSON.parse(portfolioDataElement.getAttribute("data-portfolio"))
    : [];
const allStocks = allStocksDataElement.getAttribute("data-all-stocks")
    ? JSON.parse(allStocksDataElement.getAttribute("data-all-stocks"))
    : [];

    const stockList = document.getElementById("stock-list");
    const buyModeBtn = document.getElementById("buy-mode");
    const sellModeBtn = document.getElementById("sell-mode");
    const stockListTitle = document.getElementById("stock-list-title");
    const transactionForm = document.getElementById("transaction-form");
    const transactionAction = document.getElementById("transaction-action"); // Action input field
    const buySellModalElement = document.getElementById("buySellModal");
    const confirmationModalElement = document.getElementById("confirmationModal");
    let isBuyMode = false; // Toggle buy/sell mode
    const balanceForm = document.getElementById("balance-form");
    const balanceAction = document.getElementById("balance-action");
    const depositBtn = document.getElementById("depositFundsBtn");
    const withdrawBtn = document.getElementById("withdrawFundsBtn");

    // Initialize Bootstrap modals
    const buySellModal = new bootstrap.Modal(buySellModalElement);
    const confirmationModal = new bootstrap.Modal(confirmationModalElement);

    // Extract theme colors from CSS variables
    const primaryColor = getComputedStyle(document.documentElement).getPropertyValue("--bs-primary").trim();
    const secondaryColor = getComputedStyle(document.documentElement).getPropertyValue("--bs-secondary").trim();

    // 2. CHART HANDLING
    // -----------------
    // Initialize the chart
    const ctx = document.getElementById("chart-canvas").getContext("2d");
    let stockChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Stock Price",
            data: [],
            borderColor: primaryColor,
            backgroundColor: primaryColor + "33", // Semi-transparent
            borderWidth: 2,
            fill: true,
            tension: 0.1, // Slight curve
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          x: { title: { display: true, text: "Time", color: secondaryColor } },
          y: { title: { display: true, text: "Price ($)", color: primaryColor } },
        },
        plugins: {
          legend: { labels: { color: primaryColor } },
          tooltip: {
            backgroundColor: primaryColor,
            titleColor: "#fff",
            bodyColor: "#fff",
          },
        },
      },
    });

    // Update the stock history chart
    function updateChart(history) {
      const labels = history.map((entry) => entry.timestamp);
      const prices = history.map((entry) => entry.price);

      stockChart.data.labels = labels;
      stockChart.data.datasets[0].data = prices;
      stockChart.update();
    }

    // 3. STOCK LIST HANDLING
    // ----------------------
    // Populate initial list of owned stocks
    populateStockList(portfolioStocks, false);

    // Toggle between Buy and Sell mode
    buyModeBtn.addEventListener("click", function () {
      isBuyMode = true;
      stockListTitle.textContent = "All Stocks";
      populateStockList(allStocks, true);
      buyModeBtn.classList.add("disabled");
      sellModeBtn.classList.remove("disabled");
    });

    sellModeBtn.addEventListener("click", function () {
      isBuyMode = false;
      stockListTitle.textContent = "Owned Stocks";
      populateStockList(portfolioStocks, false);
      sellModeBtn.classList.add("disabled");
      buyModeBtn.classList.remove("disabled");
    });

    // Populate stock list based on mode
    function populateStockList(stocks, isBuyMode) {
      stockList.innerHTML = ""; // Clear list
      stocks.forEach((stock) => addStockItem(stock, isBuyMode));
    }

    // Add individual stock item to list
    function addStockItem(stock, isBuyMode) {
      const listItem = document.createElement("li");
      listItem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center", "stock-item");
      listItem.dataset.stockId = stock.id;
      listItem.dataset.stockSymbol = stock.symbol;

      listItem.innerHTML = `
        ${"$" + stock.symbol} - ${stock.company || stock.name}
        <span class="badge bg-primary rounded-pill">${stock.quantity || stock.shares}</span>
        <button class="btn btn-sm btn-outline-secondary buy-sell-btn">${isBuyMode ? "Buy" : "Sell"}</button>
      `;

      // Set button click behavior
      listItem.querySelector(".buy-sell-btn").addEventListener("click", function (e) {
        e.stopPropagation();
        openTransactionModal(stock.id, stock.symbol);
      });

      // Update chart on item click
      listItem.addEventListener("click", function () {
        if (stock.history) updateChart(stock.history);
      });

      stockList.appendChild(listItem);
    }

    // 4. TRANSACTION LOGIC
    // --------------------
    // Open transaction modal and set form values
    function openTransactionModal(stockId, stockSymbol) {
      document.getElementById("transaction-stock-id").value = stockId;
      document.getElementById("transaction-stock-symbol").value = stockSymbol;
      document.getElementById("buySellModalLabel").textContent = isBuyMode ? "Buy Stock" : "Sell Stock";
      transactionAction.value = isBuyMode ? "buy" : "sell"; // Set action type
      buySellModal.show();
    }

    // Handle form submission
    transactionForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const formData = new FormData(transactionForm);

      // Log form data
      console.log("Submitting form data:");
      for (const [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
      }

      fetch("{{ url_for('web.transaction') }}", {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            showConfirmationModal(data.details);
            transactionForm.reset(); // Clear form fields
            buySellModal.hide();
          } else {
            alert(data.message);
          }
        })
        .catch((error) => console.error("Error:", error));
    });

    // Show confirmation modal
    function showConfirmationModal(details) {
      document.getElementById("order-number").textContent = details.order_number;
      document.getElementById("order-symbol").textContent = details.symbol;
      document.getElementById("order-action").textContent = isBuyMode ? "Buy" : "Sell";
      document.getElementById("order-quantity").textContent = details.quantity;
      document.getElementById("order-price").textContent = details.price;
      document.getElementById("order-total").textContent = details.total_price;
      confirmationModal.show();
    }

    // 5. BALANCE HANDLING
    // ----------------
    // Handle balance form submission

    // Set the balance action type
    function setBalanceAction(action) {
     document.getElementById("balance-action").value = action;
    }

    depositBtn.addEventListener("click", function (e) {
      e.preventDefault();
      setBalanceAction('deposit');
      submitBalanceForm();
    });

    withdrawBtn.addEventListener("click", function (e) {
      e.preventDefault();
      setBalanceAction('withdraw');
      submitBalanceForm();
    });

    // Handle form submission
    function submitBalanceForm() {
      const formData = new FormData(balanceForm);

      fetch("{{ url_for('web.update_balance') }}", {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" }
      })
        .then((response) => {
          if (!response.ok) throw new Error("Network response was not ok");
          return response.json();
        })
        .then((data) => {
          if (data.status === "success") {
            // Close the update balance modal
            const balanceModal = bootstrap.Modal.getInstance(document.getElementById("balanceModal"));
            if (balanceModal) balanceModal.hide();

            // Update the balance display
            document.getElementById("balance-display").textContent = data.details.new_balance.toFixed(2);

            // Show the confirmation modal
            showBalConfirmationModal(data.details);
            balanceForm.reset();  // Clear form fields
          } else {
            alert(data.message);
          }
        })
        .catch((error) => console.error("Error:", error));
    }

  // Show balance confirmation modal
  function showBalConfirmationModal(details) {
    document.getElementById("balConfirmationModalLabel").textContent = details.action === "deposit" ? "Funds Deposited" : "Funds Withdrawn";
    document.getElementById("bal-order-number").textContent = details.order_number;
    document.getElementById("bal-order-action").textContent = details.action === "deposit" ? "Deposit" : "Withdrawal";
    document.getElementById("bal-order-amount").textContent = details.amount.toFixed(2);
    document.getElementById("bal-order-balance").textContent = details.new_balance.toFixed(2);

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById("balConfirmationModal"));
    modal.show();
  }
});