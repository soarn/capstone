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
  
  const market_status = document.getElementById("market-status").getAttribute("data-status");
  
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
  const tertiaryColor = getComputedStyle(document.documentElement).getPropertyValue("--bs-tertiary").trim();
  const successColor = getComputedStyle(document.documentElement).getPropertyValue("--bs-success").trim();
  const dangerColor = getComputedStyle(document.documentElement).getPropertyValue("--bs-danger").trim();
  const textColor = getComputedStyle(document.documentElement).getPropertyValue("--bs-body-color").trim();
  
  // 2. CHART HANDLING
  // -----------------

  const chartContainer = document.getElementById("chart-container");
  let selectedPeriod = "1D"; // Default to 1 day
  let currentStockId = null;

  // Initialize the chart
  const chart = LightweightCharts.createChart(chartContainer, {
    width: chartContainer.offsetWidth,
    height: 400,
    layout: {
      backgroundColor: primaryColor + "33", // Semi-transparent,
      textColor: textColor,
    },
    grid: {
      vertLines: { color: tertiaryColor },
      horzLines: { color: secondaryColor },
    },
    crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
    rightPriceScale: { borderVisible: false },
    timeScale: { borderVisible: false },
  });

  const lineSeries = chart.addLineSeries({
    color: primaryColor,
    lineWidth: 2,
  });

  // Fetch stock history data
  function fetchStockData(stockId, period) {
    fetch(`/api/v1/stock-history/${period}?stock_id=${stockId}`)
    .then((response) => {
      if (!response.ok) throw new Error(`API error: ${response.status} ${response.statusText}`);
      return response.json();
    })
    .then((data) => {
      console.log("Fetched Data:", data);
      const history = data.history || [];
      const transactions = data.transactions || [];
      updateChart(history);
      updateVolumeChart(history);
      // addTransactionMarkers(transactions);
    })
    .catch((error) => {
      console.error("Error fetching stock data:", error);
      chartContainer.textContent = "Failed to load data. Please try again.";
      lineSeries.setData([]); // Clear the chart
    });
  }
  
  // Update the stock history chart
  function updateChart(history) {
    console.log("Raw history data:", history);
  
    if (!history || history.length === 0) {
      console.warn("No history data available.");
      lineSeries.setData([]); // Clear the chart
      return;
    }

    // Format the data
    const formattedData = history.map((entry) => ({
      // time: Math.floor(new Date(entry.timestamp).getTime() / 1000), // Convert timestamp to Unix format
      time: entry.timestamp_unix,
      value: parseFloat(entry.price),
    }));

    console.log("Formatted chart data:", formattedData);

    // Render the data
    lineSeries.setData(formattedData);
  }

  // Update the stock volume chart
  const volumeSeries = chart.addHistogramSeries({
    color: successColor,
    priceScaleId: '',
    lineWidth: 1,
    priceFormat: {
      type: 'volume',
    },
    overlay: true,
    scaleMargins: {
      top: 0.8,
      bottom: 0,
    },
  });

  function updateVolumeChart(history) {
    const volumeData = history.map((entry) => ({
      time: entry.timestamp_unix,
      value: entry.volume,
      
    }))
  }

  // Add markers for buy/sell transactions
  // function addTransactionMarkers(transactions) {
    // const markers = transactions
    // .filter((txn) => txn.timestamp_unix && txn.price !== null)
    // .map((txn) => ({
      // time: txn.timestamp_unix,
      // position: txn.type === "buy" ? "belowBar" : "aboveBar",
      // color: txn.type === "buy" ? successColor : dangerColor,
      // shape: txn.type === "buy" ? "arrowUp" : "arrowDown",
      // text: `${txn.type.toUpperCase()} ${txn.quantity} @ $${txn.price}`,
    // }));
    // lineSeries.setMarkers(markers);
  // }
// # TODO: SEE IF THIS IS DUPLICATING
  // Handle time period selection
  document.getElementById("time-period").addEventListener("change", function (event) {
    const period = event.target.value;
    console.log("Selected period:", period);
    selectedPeriod = period;
    if (currentStockId) fetchStockData(currentStockId, selectedPeriod);
  });

  // Handle window resize
  window.addEventListener("resize", () => {
    chart.resize(chartContainer.offsetWidth, 400);
    // chart.resize(chartContainer.offsetWidth, chartContainer.offsetHeight || 400);
  });
  console.log("Chart Container Dimensions:", chartContainer.offsetWidth, chartContainer.offsetHeight);
  
  // 3. STOCK LIST HANDLING
  // ----------------------
  // Populate initial list of owned stocks
  populateStockList(portfolioStocks, false);
  if (portfolioStocks.length > 0) {
    currentStockId = portfolioStocks[0].id; // Default to the first stock
    fetchStockData(currentStockId, selectedPeriod);
  }
  
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
       if (market_status === "closed") actionButton.classList.add("disabled");
       else {
        actionButton.addEventListener("click", (e) => {
            e.stopPropagation();
            openTransactionModal(stock.id, stock.symbol);
        });
      }

      // Append badge and button to button column
      buttonCol.appendChild(badge);
      buttonCol.appendChild(actionButton);

      // Append stock info and button columns to the list item
      listItem.appendChild(stockInfoCol);
      listItem.appendChild(buttonCol);

      // Update chart on item click
      listItem.addEventListener("click", function () {
        if (stock.id) {
          currentStockId = stock.id; // Set current stock ID
          fetchStockData(stock.id, selectedPeriod); // Fetch data
        } else {
          console.warn("Invalid stock ID:", stock);
        }
      });
      
      // Append list item to stock list
      stockList.appendChild(listItem);
    });
  }
  
  // 4. TRANSACTION LOGIC
  // --------------------
  // Open transaction modal and set form values
  if (market_status === "open") {
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
          buySellModal.hide();
          transactionForm.reset(); // Clear form fields
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
  }
});
