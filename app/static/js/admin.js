// Import CSS Files
import "datatables.net-dt/css/dataTables.dataTables.min.css"; // DataTables CSS

// Import Node.js modules installed via npm

document.addEventListener('DOMContentLoaded', async function () {
  // Initialize Choices.js for day selection
  const openDaysElement = document.getElementById('open-days');
  if (openDaysElement) {
    const { default: Choices } = await import('choices.js'); // Dynamically load Choices.js
    new Choices(openDaysElement, {
      removeItemButton: true,
      placeholderValue: 'Select Open Days',
    });
  }

  // Get user pagination setting from data attributes
  const userPagination = parseInt(document.body.dataset.userPagination, 10);

  // Define the available length options
  let lengthOptions = [
    10,
    25,
    50,
    { label: 'All', value: -1 },
  ];

  // Filter out the user's current setting from length options
  lengthOptions = lengthOptions.filter((option) =>
    typeof option === 'object'
      ? option.value !== userPagination
      : option !== userPagination
  );

  // Add the user's setting at the beginning of the menu
  lengthOptions.unshift(userPagination);

  // Initialize DataTables for transaction history
  const transactionsTable = document.getElementById('transactions-table');
  if (transactionsTable) {
    const { default: DataTable } = await import('datatables.net'); // Dynamically load DataTables
    $('#transactions-table').DataTable({
     processing: true,
      serverSide: true,
      ajax: {
        url: document.body.dataset.transactionDataUrl,
        type: 'GET',
      },
      pageLength: userPagination,
      lengthMenu: lengthOptions,
      columns: [
        { data: 'order_number' },
        { data: 'username' },
        { data: 'symbol' },
        { data: 'type' },
        { data: 'quantity' },
        {
          data: 'price',
          render: $.fn.dataTable.render.number(',', '.', 2, '$'),
        },
        {
          data: 'amount',
          render: $.fn.dataTable.render.number(',', '.', 2, '$'),
        },
        {
          data: 'timestamp',
          render: $.fn.dataTable.render('lll'),
        },
      ],
      order: [[7, 'desc']], // Sort by the timestamp column, descending
    });
  }
});

