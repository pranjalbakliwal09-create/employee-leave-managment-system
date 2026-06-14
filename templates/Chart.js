<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<canvas id="leaveChart"></canvas>
<script>

new Chart(document.getElementById('leaveChart'), {
    type: 'bar',
    data: {
        labels: ['Approved', 'Rejected', 'Pending'],
        datasets: [{
            label: 'Leave Requests',
            data: [12, 5, 3]
        }]
    }
})

</script>