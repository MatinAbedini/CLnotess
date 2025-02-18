$(document).ready(function() {
    Morris.Bar({
        element: 'morris_bar_chart',
        data: [{
            device: 'iPhone',
            geekbench: 136
        }, {
            device: 'iPhone 3G',
            geekbench: 137
        }, {
            device: 'iPhone 3GS',
            geekbench: 275
        }, {
            device: 'iPhone 4',
            geekbench: 380
        }, {
            device: 'iPhone 4S',
            geekbench: 655
        }, {
            device: 'iPhone 5',
            geekbench: 1571
        }],
        xkey: 'label',
        ykeys: ['value'],
        labels: ['Value'],
        barColors: ['#635bd6'],
        hideHover: 'auto',
        resize: true
    });
});
