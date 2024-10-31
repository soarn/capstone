document.addEventListener("DOMContentLoaded", function () {
  // 1. INITIALIZATION
  // -----------------
  const portfolioDataElement = document.getElementById("portfolio-data");
  const allStocksDataElement = document.getElementById("all-stocks-data");

  // Get endpoint URLs from HTML
  const transactionEndpoint = document.getElementById("transaction-endpoint").getAttribute("data-url");
  const balanceEndpoint = document.getElementById("balance-endpoint").getAttribute("data-url");
  
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
  
  function populateStockList(stocks, isBuyMode) {
    stockList.innerHTML = ""; // Clear list
    
    stocks.forEach((stock) => {
      const listItem = document.createElement("li");
      listItem.classList.add("list-group-item");

      // Create the row for layout
      const row = document.createElement("div");
      row.classList.add("row", "w-100");

      // Column for stock symbol and name
      const stockInfoCol = document.createElement("div");
      stockInfoCol.classList.add("stock-info");
      stockInfoCol.innerHTML = `<strong>$${stock.symbol}</strong> - ${stock.name || stock.company || 'undefined'}`;

       // Column for quantity badge and button (right-aligned)
       const buttonCol = document.createElement("div");
       buttonCol.classList.add("button-col");

       // Quantity Badge
       const badge = document.createElement("span");
       badge.classList.add("badge", "bg-primary", "rounded-pill", "quantity-badge");
       badge.textContent = stock.shares || stock.quantity || 'undefined';

       // Buy/Sell button
       const actionButton = document.createElement("button");
       actionButton.classList.add("btn", "btn-sm", "btn-outline-secondary", "buy-sell-btn");
       actionButton.textContent = isBuyMode ? "BUY" : "SELL";
       actionButton.addEventListener("click", (e) => {
           e.stopPropagation();
           openTransactionModal(stock.id, stock.symbol);
       });

      // Append badge and button to button column
      buttonCol.appendChild(badge);
      buttonCol.appendChild(actionButton);

      // Append stock info and button columns to the list item
      listItem.appendChild(stockInfoCol);
      listItem.appendChild(buttonCol);

      // Update chart on item click
      listItem.addEventListener("click", function () {
          if (stock.history) updateChart(stock.history);
      });

      // Append list item to stock list
      stockList.appendChild(listItem);
    });
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
    
    fetch(transactionEndpoint, {  // Using the endpoint URL
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
  
  function submitBalanceForm() {
    const formData = new FormData(balanceForm);
    
    fetch(balanceEndpoint, {  // Using the endpoint URL
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
        const balanceModal = bootstrap.Modal.getInstance(document.getElementById("balanceModal"));
        if (balanceModal) balanceModal.hide();
        document.getElementById("balance-display").textContent = data.details.new_balance.toFixed(2);
        showBalConfirmationModal(data.details);
        balanceForm.reset();
      } else {
        alert(data.message);
      }
    })
    .catch((error) => console.error("Error:", error));
  }
  
  function showBalConfirmationModal(details) {
    document.getElementById("balConfirmationModalLabel").textContent = details.action === "deposit" ? "Funds Deposited" : "Funds Withdrawn";
    document.getElementById("bal-order-number").textContent = details.order_number;
    document.getElementById("bal-order-action").textContent = details.action === "deposit" ? "Deposit" : "Withdrawal";
    document.getElementById("bal-order-amount").textContent = details.amount.toFixed(2);
    document.getElementById("bal-order-balance").textContent = details.new_balance.toFixed(2);
    const modal = new bootstrap.Modal(document.getElementById("balConfirmationModal"));
    modal.show();
  }
});
