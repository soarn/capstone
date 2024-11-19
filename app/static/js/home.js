// Import CSS Files
import "datatables.net-dt/css/dataTables.dataTables.min.css"; // DataTables CSS

document.addEventListener("DOMContentLoaded", async () => {
  const { default: DataTable } = await import("datatables.net"); // Dynamically load DataTables
  // Retrieve dynamic data from HTML
  const stockTableElement = document.getElementById("stock-table");

  if (stockTableElement) {
    // Get user pagination setting from data attributes
    const userPagination = parseInt(stockTableElement.dataset.pagination, 10) || 10;

    // Define available length options
    let lengthOptions = [
      10,
      25,
      50,
      { label: "All", value: -1 },
    ];

    // Filter out user's current setting from length options
    lengthOptions = lengthOptions.filter((option) =>
      typeof option === "object"
        ? option.value !== userPagination
        : option !== userPagination
    );

    // Add user's pagination setting at the beginning of the menu
    lengthOptions.unshift(userPagination);

   // Initialize DataTables for the stock table
    $(stockTableElement).DataTable({
      processing: true,
      serverSide: true,
      ajax: {
        url: stockTableElement.dataset.url, // Fetch the AJAX URL dynamically
        type: "GET",
      },
      pageLength: userPagination,
      lengthMenu: lengthOptions,
      columns: [
        { data: "symbol" },
        { data: "company" },
        {
          data: "price",
          render: $.fn.dataTable.render.number(",", ".", 2, "$"),
        },
        { data: "quantity" },
        {
          data: "open_price",
          render: $.fn.dataTable.render.number(",", ".", 2, "$"),
        },
        {
          data: "high_price",
          render: $.fn.dataTable.render.number(",", ".", 2, "$"),
        },
        {
          data: "low_price",
          render: $.fn.dataTable.render.number(",", ".", 2, "$"),
        },
        {
          data: "close_price",
          render: $.fn.dataTable.render.number(",", ".", 2, "$"),
        },
        { data: "volume" },
     ],
      order: [[7, "desc"]],
    });
  }
});

