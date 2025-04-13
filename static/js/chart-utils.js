/**
 * Helper functions for Chart.js charts
 */

// Default chart colors
const chartColors = [
    'rgba(75, 192, 192, 0.8)',
    'rgba(54, 162, 235, 0.8)',
    'rgba(255, 206, 86, 0.8)',
    'rgba(255, 99, 132, 0.8)',
    'rgba(153, 102, 255, 0.8)',
    'rgba(255, 159, 64, 0.8)',
    'rgba(201, 203, 207, 0.8)',
    'rgba(0, 204, 150, 0.8)'
];

// Alternative darker colors for borders
const borderColors = [
    'rgba(75, 192, 192, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(255, 99, 132, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)',
    'rgba(201, 203, 207, 1)',
    'rgba(0, 204, 150, 1)'
];

/**
 * Creates a bar chart in the specified element
 * @param {string} elementId - The ID of the canvas element
 * @param {string} title - Chart title
 * @param {Array} labels - Array of labels
 * @param {Array} data - Array of data values
 * @param {string} xLabel - X-axis label
 * @param {string} yLabel - Y-axis label
 */
function createBarChart(elementId, title, labels, data, xLabel, yLabel) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const backgroundColors = data.map((_, index) => chartColors[index % chartColors.length]);
    const borderColorList = data.map((_, index) => borderColors[index % borderColors.length]);
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: backgroundColors,
                borderColor: borderColorList,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false,
                },
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                x: {
                    title: {
                        display: xLabel !== '',
                        text: xLabel
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: yLabel !== '',
                        text: yLabel
                    }
                }
            }
        }
    });
}

/**
 * Creates a doughnut chart in the specified element
 * @param {string} elementId - The ID of the canvas element
 * @param {string} title - Chart title
 * @param {Array} labels - Array of labels
 * @param {Array} data - Array of data values
 */
function createDoughnutChart(elementId, title, labels, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const backgroundColors = data.map((_, index) => chartColors[index % chartColors.length]);
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            }
        }
    });
}

/**
 * Creates a pie chart in the specified element
 * @param {string} elementId - The ID of the canvas element
 * @param {string} title - Chart title
 * @param {Array} labels - Array of labels
 * @param {Array} data - Array of data values
 */
function createPieChart(elementId, title, labels, data) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const backgroundColors = data.map((_, index) => chartColors[index % chartColors.length]);
    
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            }
        }
    });
}

/**
 * Load data from an API endpoint and create a chart
 * @param {string} apiUrl - The API URL to fetch data from
 * @param {string} chartType - The type of chart to create (bar, doughnut, pie)
 * @param {string} elementId - The ID of the canvas element
 * @param {string} title - Chart title
 * @param {string} xLabel - X-axis label (for bar charts)
 * @param {string} yLabel - Y-axis label (for bar charts)
 */
function loadChartData(apiUrl, chartType, elementId, title, xLabel = '', yLabel = '') {
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            if (chartType === 'bar') {
                createBarChart(elementId, title, data.labels, data.data, xLabel, yLabel);
            } else if (chartType === 'doughnut') {
                createDoughnutChart(elementId, title, data.labels, data.data);
            } else if (chartType === 'pie') {
                createPieChart(elementId, title, data.labels, data.data);
            }
        })
        .catch(error => {
            console.error('Error loading chart data:', error);
            const canvas = document.getElementById(elementId);
            const container = canvas.parentElement;
            container.innerHTML = `<div class="alert alert-danger">Failed to load chart data: ${error.message}</div>`;
        });
}
