//Under main.js

// Plot. R updated with user selected values via R.setP()
let plot = new Plot(plotParams,R)
calcPlot();
plot.draw();

function calcPlot(){
    let optVal = optArrayPlot.filter(x=>x.selected)[0].value; // selected plot option
    if (optVal == 0){
        plot.calc_yx_constP();
    } else if (optVal == 1){
        plot.calc_yx_constT();
    } else if (optVal == 2){
        plot.calc_Txy();
    } else if (optVal == 3){
        plot.calc_Pxy();
    }
}

function updatePlot(){
    if (plot.replot_scheduled){
        calcPlot(); 
        plot.draw();
    }
}