// Import Node.js modules installed via npm
const launchConfetti = () => import('canvas-confetti'); // Confetti Library
import { createChart, CrosshairMode, LineStyle } from "lightweight-charts"; // Chart Library
import Popper from "@popperjs/core"; // Popper for Bootstrap Popover

// Importing CSS files
import 'choices.js/public/assets/styles/choices.min.css'; // Choices.js styles


// IMPORTANT: IN THIS FILE, 'VOLUME' REFERS TO THE MARKET CAP!!
document.addEventListener("DOMContentLoaded", function () {

  // Function to get the cookie value
  function getCookie(name) {
    const value = `;${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }
  
  // 1. INITIALIZATION
  // -----------------
  const portfolioDataElement = document.getElementById("portfolio-data");
  const allStocksDataElement = document.getElementById("all-stocks-data");

  // Get endpoint URLs from HTML
  const transactionEndpoint = document
    .getElementById("transaction-endpoint")
    .getAttribute("data-url");
  const balanceEndpoint = document
    .getElementById("balance-endpoint")
    .getAttribute("data-url");

  // Get market status from HTML
  const market_status = document
    .getElementById("market-status")
    .getAttribute("data-status");

  // Check if data attributes exist and are not empty before parsing
  const portfolioStocks = portfolioDataElement.getAttribute("data-portfolio")
    ? JSON.parse(portfolioDataElement.getAttribute("data-portfolio"))
    : [];
  const allStocks = allStocksDataElement.getAttribute("data-all-stocks")
    ? JSON.parse(allStocksDataElement.getAttribute("data-all-stocks"))
    : [];
  
  // Check if the user has confetti enabled
  const confettiEnabled = document.getElementById("confetti-enabled").getAttribute("data-confetti");

  let isBuyMode = false; // Toggle buy/sell mode

  // DOM elements
  const stockList = document.getElementById("stock-list");
  const buyModeBtn = document.getElementById("buy-mode");
  const sellModeBtn = document.getElementById("sell-mode");
  const stockListTitle = document.getElementById("stock-list-title");
  const transactionForm = document.getElementById("transaction-form");
  const transactionAction = document.getElementById("transaction-action"); // Action input field
  const buySellModalElement = document.getElementById("buySellModal");
  const confirmationModalElement = document.getElementById("confirmationModal");
  const balanceConfirmationModalElement = document.getElementById("balConfirmationModal");
  const balanceForm = document.getElementById("balance-form");
  const balanceAction = document.getElementById("balance-action");
  const depositBtn = document.getElementById("depositFundsBtn");
  const withdrawBtn = document.getElementById("withdrawFundsBtn");
  const timePeriodSelector = document.getElementById("time-period");

  // Initialize Bootstrap modals
  const buySellModal = new bootstrap.Modal(buySellModalElement);
  const confirmationModal = new bootstrap.Modal(confirmationModalElement);

  // Extract theme colors from CSS variables
  const primaryColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-primary")
    .trim();
  const secondaryColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-secondary")
    .trim();
  const tertiaryColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-tertiary")
    .trim();
  const successColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-success")
    .trim();
  const dangerColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-danger")
    .trim();
  const warningColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-warning")
    .trim();
  const infoColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-info")
    .trim();
  const textColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-body-color")
    .trim();
  const bodyBgColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-body-bg")
    .trim();
  const redColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-red")
    .trim();
  const greenColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-green")
    .trim();
  const blueColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-blue")
    .trim();
  const yellowColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-yellow")
    .trim();
  const purpleColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-purple")
    .trim();
  const cyanColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-cyan")
    .trim();
  const orangeColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-orange")
    .trim();
  const pinkColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-pink")
    .trim();
  const tealColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-teal")
    .trim();
  const indigoColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-indigo")
    .trim();
  const limeColor = getComputedStyle(document.documentElement)
    .getPropertyValue("--bs-lime")
    .trim();

  // 2. CHART HANDLING
  // -----------------

  const chartContainer = document.getElementById("chart-container");
  let selectedPeriod = "1D"; // Default to 1 day
  let currentStockId = null;

  // Custom Formatters
  const usdPriceFormatter = Intl.NumberFormat(getCookie("user_locale"), {
    style: 'currency',
    currency: 'USD',
  }).format;

  // Initialize the chart
  const chart = createChart(chartContainer, {
    width: chartContainer.offsetWidth,
    height: 400,
    layout: {
      background: { type: 'solid', color: 'transparent' },
      textColor: textColor,
    },
    grid: {
      vertLines: { color: secondaryColor },
      horzLines: { color: secondaryColor },
    },
    crosshair: { mode: CrosshairMode.Normal },
    rightPriceScale: { borderVisible: false },
    timeScale: { 
      borderVisible: false,
      timeVisible: true,
      barSpacing: 10,
      localization: {
        timeFormatter: (timestamp) => {
          const date = new Date(timestamp * 1000);
          return date.toLocaleString(getCookie("user_locale"), {
            timeZone: getCookie("user_time_zone")
          });
        },
      },
    },
    localization: {
      timeFormatter: (timestamp) => {
        const date = new Date(timestamp * 1000);
        return date.toLocaleString(getCookie("user_locale"), {
          timeZone: getCookie("user_time_zone")
        });
      },
    },
  });

  // Set the border color for the vertical axis
  chart.priceScale().applyOptions({
    borderColor: infoColor,
  });

  // Set the border color for the horizontal axis
  chart.timeScale().applyOptions({
    borderColor: infoColor,
    barSpacing: 10,
  });

  // Apply the custom usdPriceFormatter to the chart
  chart.applyOptions({
    localization: {
      priceFormatter: usdPriceFormatter,
    },
  });

  // Customize the Crosshair
  chart.applyOptions({
    crosshair: {
      mode: CrosshairMode.Normal,

      // Vertical crosshair line (showing Date in Label)
      vertLine: {
        width: 8,
        color: purpleColor + '33',
        style: LineStyle.Solid,
        labelBackgroundColor: yellowColor,
      },

      // Horizontal crosshair line (showing Price in Label)
      horzLine: {
        color: yellowColor,
        labelBackgroundColor: yellowColor,
      },
    },
  });

  chart.timeScale().fitContent();

  // Add candlestick series for OHLC data
  const candlestickSeries = chart.addCandlestickSeries({
    upColor: successColor,
    downColor: dangerColor,
    borderUpColor: successColor,
    borderDownColor: dangerColor,
    wickUpColor: successColor,
    wickDownColor: dangerColor,
  });

  // Add an area series to the chart,
  // Adding this before we add the candlestick cghart
  // so that it will appear beneath the candlesticks
  const areaSeries = chart.addAreaSeries({
    lastValueVisible: false, // hide the last value marker for this series
    crosshairMarkervisible: false, // hide the crosshair marker for this series
    lineColor: "transparent", // hide the line
    topColor: purpleColor + 33,
    bottomColor: purpleColor + 11,
  });

  // Add volume series
  const volumeSeries = chart.addLineSeries({
    color: warningColor,
    priceScaleId: "",
    priceFormat: { type: "volume" },
  });

  // Configure the secondary price scale for volume
  chart.priceScale("volume").applyOptions({
    position: "left",
    scaleMargins: {
      top: 0.8,
      bottom: 0,
    },
  });

  // 3. FETCH AND UPDATE CHART DATA
  // -----------------

  // Fetch stock data from the API
  function fetchStockData(stockId, period) {
    fetch(`/api/v1/stock-history/${period}?stock_id=${stockId}`)
      .then((response) => {
        if (!response.ok)
          throw new Error(
            `API error: ${response.status} ${response.statusText}`
          );
        return response.json();
      })
      .then((data) => {
        console.log("Fetched Data:", data);
        const history = data.history || [];
        const transactions = data.transactions || [];
        updateCandlestickChart(history);
        updateVolumeChart(history);
      })
      .catch((error) => {
        console.error("Error fetching stock data:", error);
        chartContainer.textContent = "Failed to load data. Please try again.";
        candlestickSeries.setData([]); // Clear the chart
        volumeSeries.setData([]);
      });
  }

  // Update the candlestick chart with OHLC data
  function updateCandlestickChart(history) {
    if (!history || history.length === 0) {
      console.warn("No history data available.");
      candlestickSeries.setData([]); // Clear the chart
      return;
    }

    const validCandlestickData = history.filter(
      (entry) =>
        entry.timestamp_unix &&
        entry.open_price !== null &&
        entry.high_price !== null &&
        entry.low_price !== null &&
        entry.close_price !== null &&
        entry.volume !== null
    );

    // Format the candlestick data
    const candlestickData = validCandlestickData.map((entry) => ({
      time: entry.timestamp_unix,
      open: parseFloat(entry.open_price),
      high: parseFloat(entry.high_price),
      low: parseFloat(entry.low_price),
      close: parseFloat(entry.close_price),
      volume: entry.volume,
    }));

    // Format the areaSeries
    const lineData = validCandlestickData.map((datapoint) => ({
      time: datapoint.timestamp_unix,
      value: (parseFloat(datapoint.close_price) + parseFloat(datapoint.open_price)) / 2,
    }));

    // Set the data for the Area Series
    areaSeries.setData(lineData)

    console.log("Formatted candlestick data:", candlestickData);

    candlestickSeries.setData(candlestickData);
  }

  // Update the volume chart
  function updateVolumeChart(history) {
    if (!history || history.length === 0) {
      console.warn("No history data available.");
      volumeSeries.setData([]); // Clear the chart
      return;
    }

    // Format the data for the volume chart
    const volumeData = history.map((entry) => ({
      time: entry.timestamp_unix,
      value: parseInt(entry.volume, 10),
      color: entry.close_price > entry.open_price ? infoColor : warningColor,
    }));

    console.log("Formatted volume data:", volumeData);

    volumeSeries.setData(volumeData);
  }

  // 4. HANDLE USER INTERACTIONS
  // ---------------------------

  // Time period selector
  timePeriodSelector.addEventListener("click", function (event) {
    const button = event.target.closest("button[data-period]");
    if (button) {
      const period = button.getAttribute("data-period");
      selectedPeriod = period;
      console.log("Selected period:", selectedPeriod);
      if (currentStockId) fetchStockData(currentStockId, selectedPeriod);
    }
  });

  // Resize chart on window resize
  window.addEventListener("resize", () => {
    chart.resize(chartContainer.offsetWidth, 400);
  });

  // 5. STOCK LIST HANDLING
  // ----------------------
  // Populate initial list of owned stocks or all stocks if portfolio is empty
  if (portfolioStocks.length > 0) {
    populateStockList(portfolioStocks, false);
    currentStockId = portfolioStocks[0].id; // Default to the first stock
    fetchStockData(currentStockId, selectedPeriod);
    sellModeBtn.classList.add("disabled");
    document.getElementById("buySellModalLabel").textContent = "Sell Stock";
    isBuyMode = false;
  } else {
    populateStockList(allStocks, true);
    currentStockId = allStocks[0].id; // Default to the first stock
    fetchStockData(currentStockId, selectedPeriod);
    this.getElementById('stock-list-title').textContent = "All Stocks";
    buyModeBtn.classList.add("disabled");
    document.getElementById("buySellModalLabel").textContent = "Buy Stock";
    isBuyMode = true;
  }

  // Toggle between Buy and Sell mode
  buyModeBtn.addEventListener("click", function () {
    isBuyMode = true;
    stockListTitle.textContent = "All Stocks";
    populateStockList(allStocks, true);
    buyModeBtn.classList.add("disabled");
    sellModeBtn.classList.remove("disabled");
    feather.replace();
  });

  sellModeBtn.addEventListener("click", function () {
    isBuyMode = false;
    stockListTitle.textContent = "Owned Stocks";
    populateStockList(portfolioStocks, false);
    sellModeBtn.classList.add("disabled");
    buyModeBtn.classList.remove("disabled");
    feather.replace();
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
      stockInfoCol.innerHTML = `<strong>$${stock.symbol}</strong><i id="themeIcon" data-feather="chevron-right"></i> ${
        stock.name || stock.company || "undefined"
      } <i id="themeIcon" data-feather="chevron-right"></i> $${stock.price}`;

      // Column for quantity badge and button (right-aligned)
      const buttonCol = document.createElement("div");
      buttonCol.classList.add("button-col");

      // Quantity Badge
      const badge = document.createElement("span");
      badge.classList.add(
        "badge",
        "bg-primary",
        "rounded-pill",
        "quantity-badge"
      );
      badge.textContent = stock.shares || stock.quantity || "undefined";

      // Buy/Sell button
      const actionButton = document.createElement("button");
      actionButton.classList.add(
        "btn",
        "btn-sm",
        "btn-outline-secondary",
        "buy-sell-btn"
      );
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

  // 6. TRANSACTION LOGIC
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

  // Initialize the popover for the confirm button
  const confirmButton = document.getElementById('confirm-action');
  const popoverInstance = new bootstrap.Popover(confirmButton, {
    html: true,
    content: `
      <div class="d-flex justify-content-around">
        <a class="btn btn-success btn-sm confirm-btn">Yes</a>
        <a class="btn btn-danger btn-sm cancel-btn">No</a>
      </div>
    `,
    trigger: 'focus',
    placement: 'top',
  });

  // Event delegation to handle confirm and cancel actions inside the popover
  confirmButton.addEventListener('shown.bs.popover', function () {
    const popoverElement = document.querySelector('.popover');
    if (popoverElement) {
      const confirmBtn = popoverElement.querySelector('.confirm-btn');
      const cancelBtn = popoverElement.querySelector('.cancel-btn');

      confirmBtn.addEventListener('click', function() {
        // User clicked "Yes" - proceed with form submission
        const formData = new FormData(transactionForm);

        // Submit the form via fetch API
        fetch(transactionEndpoint, {
          method: "POST",
          body: formData,
          headers: { "X-Requested-With": "XMLHttpRequest" },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.status === "success") {
              showConfirmationModal(data.details); // Display the success modal
              if (confettiEnabled) launchConfetti(); // Trigger confetti animation if enabled
              transactionForm.reset(); // Reset form fields
              buySellModal.hide(); // Close the modal
            } else {
              alert(`Error: ${data.message}`); // Display error message
            }
          })
          .catch((error) => console.error("Error:", error));

          // Hide the popover
          popoverInstance.hide();
      });

    cancelBtn.addEventListener('click', function() {
      // User clicked "No" - close the popover
      popoverInstance.hide();
      transactionForm.reset(); // Reset form fields
      buySellModal.hide(); // Close the modal
    });
  }
  });

    // Function to launch confetti animation
    launchConfetti().then((confetti) => {
      // Basic confetti burst
      confetti({
          particleCount: 100,
          spread: 70,
          origin: { y: 0.6 } // Middle of the screen
      });

      // Add a series of confetti bursts for a better effect
      setTimeout(function() {
          confetti({
              particleCount: 100,
              spread: 120,
              origin: { y: 0.6 }
          });
      }, 200);

      setTimeout(function() {
          confetti({
              particleCount: 150,
              spread: 100,
              origin: { y: 0.6 }
          });
      }, 400);

      const colors = [redColor, greenColor, blueColor, yellowColor, purpleColor, cyanColor, orangeColor, pinkColor, tealColor, indigoColor, limeColor];
      confetti({
          particleCount: 150,
          spread: 100,
          origin: { y: 0.6 },
          colors: colors
      });

      // Additional bursts for a more exciting effect
      setTimeout(function() {
          confetti({
              particleCount: 100,
              spread: 70,
              origin: { y: 0.6 },
              colors: colors
          });
      }, 200);
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

    // Refresh the page after the modal is closed
    confirmationModalElement.addEventListener("hidden.bs.modal", function () {
      location.reload();
    });

    // 7. BALANCE HANDLING
    // ----------------
    function setBalanceAction(action) {
      document.getElementById("balance-action").value = action;
    }

    depositBtn.addEventListener("click", function (e) {
      e.preventDefault();
      setBalanceAction("deposit");
      submitBalanceForm();
    });

    withdrawBtn.addEventListener("click", function (e) {
      e.preventDefault();
      setBalanceAction("withdraw");
      submitBalanceForm();
    });

    function submitBalanceForm() {
      const formData = new FormData(balanceForm);

      fetch(balanceEndpoint, {
        // Using the endpoint URL
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
        .then((response) => {
          if (!response.ok) throw new Error("Network response was not ok");
          return response.json();
        })
        .then((data) => {
          if (data.status === "success") {
            const balanceModal = bootstrap.Modal.getInstance(
              document.getElementById("balanceModal")
            );
            if (balanceModal) balanceModal.hide();
            document.getElementById("balance-display").textContent =
              data.details.new_balance.toFixed(2);
            showBalConfirmationModal(data.details);
            balanceForm.reset();
          } else {
            alert(data.message);
          }
        })
        .catch((error) => console.error("Error:", error));
    }

    function showBalConfirmationModal(details) {
      document.getElementById("balConfirmationModalLabel").textContent =
        details.action === "deposit" ? "Funds Deposited" : "Funds Withdrawn";
      document.getElementById("bal-order-number").textContent =
        details.order_number;
      document.getElementById("bal-order-action").textContent =
        details.action === "deposit" ? "Deposit" : "Withdrawal";
      document.getElementById("bal-order-amount").textContent =
        details.amount.toFixed(2);
      document.getElementById("bal-order-balance").textContent =
        details.new_balance.toFixed(2);
      const modal = new bootstrap.Modal(
        document.getElementById("balConfirmationModal")
      );
      modal.show();
    }

    // Refresh the page after the modal is closed
    balanceConfirmationModalElement.addEventListener("hidden.bs.modal", function () {
      location.reload();
    });
  }
  feather.replace()
});
