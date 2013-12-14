/**
 * Created by milan on 12/14/13.
 */
var chartOptions = {
    backgroundColor: 'transparent', pieSliceBorderColor: 'transparent',
    fontSize: 12, fontName: 'sans-serif',
    chartArea: {width: 420, top: 0, left: 0, height: 300},
    legend: {textStyle: {color: '#000'}}
};

var suffix, colors = [];
var data = new google.visualization.DataTable();
switch(field_name) {
    case 'eqv':
        suffix = ' mm'; break;
    case 'iso':
        suffix = ' ASA'; break;
    default:
        suffix = '';
}
data.addColumn('string', 'name');
data.addColumn('number', 'count');

$.each(items, function(i, item) {
    data.addRow([item.name + suffix, item.count]);
    if (item.hex) colors.push(item.hex);
});
var chart = new google.visualization.PieChart($('#chart')[0]);
if (colors.length > 0) $.extend(chartOptions, {colors: colors});
chart.draw(data, chartOptions);
delete chartOptions['colors'];