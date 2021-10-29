/* Javascript used to start an experiment and showns graphics in real time

Developed by José Veiga and Pedro Rosa

Last updated out 9 11:12 , 2021*/


// starting all the variables
var base_url = "http://10.2.12.86:8000";
var apparatus = 4
var protocol = 5
// {
//   "apparatus": 0,
//   "protocol": 0,
//   "config": {}
// }

let execution_id = 0;
let Results=0;
var DeltaX=0;
var Samples=0;
var point_x;
var point_y;
var name = ''
var frist=0;
var point_x;
var point_y;
var output_data = [];
var receive_error_velocity = [];
var receive_error_period = [];
var mytable = [];
var DeltaX = document.getElementById('DeltaX');
var Samples = document.getElementById('Samples');


function getCookie(name) 
{
  var dc = document.cookie;
  var prefix = name + "=";
  var begin = dc.indexOf("; " + prefix);
  if (begin == -1) 
  {
    begin = dc.indexOf(prefix);
    if (begin != 0) return null;
  }
  else
  {
    begin += 2;
    var end = document.cookie.indexOf(";", begin);
    if (end == -1) 
    {
      end = dc.length;
    }
  }
  
  // because unescape has been deprecated, replaced with decodeURI
  // return unescape(dc.substring(begin + prefix.length, end));
  return decodeURI(dc.substring(begin + prefix.length, end));
}



// This function receive as input the parameters and send them to the experiment and send back the data to browser*/

function queue() {
  // get inputs values from the client side
  if ($("#DeltaX").val() !== undefined)
    DeltaX = $("#DeltaX").val();
  if ($("#Samples").val() !== undefined)
    Samples = $("#Samples").val();

  
  data_send = {"apparatus": apparatus, "protocol": protocol, "config": {"deltaX": DeltaX, "samples":Samples}}
  // '{"experiment_name": "Pendulo", "config_experiment": {"DeltaX":'+ String(DeltaX)+', "Samples":'+String(Samples)+' }}'
  HEADERS = {
    "X-CSRFToken": getCookie("csrftoken"),
    }
  var endpoint="api/v1/execution";
  // print out
  console.log('JSON : ' +  endpoint);
  console.log('JSON : ' +  data_send);

  // $.ajax({
  //   url: endpoint,   //Your api url
  //   type: 'POST',   //type is any HTTP method
  //   contentType: 'application/json;charset=UTF-8',
  //   data: JSON,
  //   success: function (response){
  //   console.log('PUT response in:' +response.id);
  //   execution_id = response.id
  //   }
  // });

  axios({
    method: 'post', //you can set what request you want to be
    url: endpoint,
    headers: HEADERS,
    data: data_send,
  }).then(response => {
    console.log('plotly_results', response);
    execution_id = response.data.id
  }).catch(console);


  // não quero fazer pontos no botão start!
  // Tenho que mudar alguma coisa aqui pois ainda não faz o que realmente quero
  // getData(); 
  


}

function start() {
  var endpoint_2="api/v1/execution/"+execution_id+"/start";
  // print out
  console.log('JSON : ' +  endpoint_2);
  // console.log('JSON : ' +  JSON);
  // data_send = {}
  // $.ajax({
  //   url: endpoint_2,   //Your api url
  //   type: 'PUT',   //type is any HTTP method
  //   contentType: 'application/json;charset=UTF-8',
  //   data: JSON,
  //   success: function (response){
  //   console.log('PUT response in:' +response);
  //   }
  // });

  axios({
    method: 'put', //you can set what request you want to be
    url: endpoint_2,
    headers: HEADERS,
  }).then(response => {
    console.log('plotly_results', response);
  }).catch(error => {
    if (error.response !== undefined) {
    console.error('Error : ', error.response.data);
    }
  });
  
  $('.menu .item').tab('change tab','execution');
}




// Receive data from experiment
function getData(){
  var endpoint =  base_url + '/resultpoint';
  $.ajax({
    url: endpoint,   //Your api url
    type: 'GET',   //type is any HTTP method
    contentType: 'application/json;charset=UTF-8',
    success: function (response){
      if (frist == 0)
		{
			res = Object.keys(response.Data);
			buildPlot1(res);
                       buildPlot2(res);  // grafico de temperatura não 
                       buildPlot3(res);
			frist = 1;
		}
      console.log(response);
      // check for ending of the experiment
      if (response.status !== 'undefined' && response.status === 'Experiment Ended'){
          myStopFunction();
      }
      else{
       
        if (typeof response.Data === 'object'){
          
          receive_error_velocity = response.Data.e_velocity;
          receive_error_period = response.Data.e_period;
          
          Plotly.extendTraces('myplot', {x: [[response.Data.Sample_number]],y: [[response.Data.velocity]],
            'error_y.array': [[ receive_error_velocity ]]}, [0]);
          Plotly.extendTraces('myplot1', {x: [[response.Data.period]]}, [0]);
          Plotly.extendTraces('myplot2', {x: [[response.Data.Sample_number]],y: [[response.Data.period]],
          'error_y.array': [[receive_error_period]]}, [0]);
    
          // tabela 
          mytable.push(response.Data);
         // create a table
          var html = "<table>";
         
           mytable.forEach(function(data) {
           for (var i in data ){
                 html += "<td>" + data[i]  +  "</td>";
           }
           html += "</tr >";
           });
           html += "</table>";
		// assumes <div id="result"></div>
           document.getElementById("result").innerHTML = html;
        }
        getData();
      }
     
    }
  });
}


/*
Não percebo porquê que não funciona com o nosso endpoint...... 'https://127.0.0.1:5000/resultpoint'!
$.ajax({
  url: base_url + '/resultpoint',
  type: "get",
  dataType: "json",

  success: function(results) {
      drawTable(results.Data);
  }
});

function drawTable(data){
  for (var i = 0; i < data.length; i++){
      drawRow(data[i]);
  }
}

function drawRow(rowData){
  var row = $("<tr />")
  $("#result").append(row);
  row.append($("<td>" + rowData.Sample_number + "</td>"));
    row.append($("<td>" + rowData.period + "</td>"));
    row.append($("<td>" + rowData.e_period + "</td>"));
 

}*/



//// nao usado
function tablebind() {  
  $.ajax({  
      type: "GET",  
      contentType: "application/json; charset=utf-8",  
      url: base_url + '/resultpoint',  
      data: "{}",  
      contentType: 'application/json;charset=UTF-8',
      success: function (response) {  
          var obj = $.parseJSON(response.d);  
          if (obj.length > 0) {  

              var data = obj[0].Table1;  
              var table = $("<table />");  
              table[0].border = "1";  

              var row$;  

              var columns = addAllColumnHeaders(data);  
              for (var i = 0; i < data.length; i++) {  
                  row$ = $('<tr/>');  
           
                  for (var colIndex = 0; colIndex < columns.length; colIndex++) {  
                      var cellValue = data[i][columns[colIndex]];  

                      if (cellValue == null) { cellValue = ""; }  

                      row$.append($('<td/>').html(cellValue));  
                  }  
                  $("#jsonTable").append(row$);  
              }  
               
          }  

      },  
      error: function (response) {  
          //                      
      }  
  });  

}  




var point_x;
var point_y;
/////////////////////////////////////////////////////////////////////////////////
//////////// Build graphic                    
/////////////////////////////////////////////////////////////////////////////////


// To improve
var selectorOptions = {
  buttons: [{
      step: '1',
      stepmode: 'backward',
      count: 1,
      label: '10N'
  },{

      step: 'all',

  }],

};


function buildPlot1(res) {

  console.log(res);
  var trace1 = {
		x: [],
		y: [],
    error_y: {
      type: 'data',
      color: '#85144B',
      array: [],
      thickness: 1.5,
      width:3,
      visible: true
    },
    mode: 'lines+markers',
    line: {
      color: "#1f77b4", 
      width: 1
    },marker: {
      color: "rgb(0, 255, 255)", 
      size: 6, 
      line: {
        color: "black", 
        width: 0.5
      }
    },
    type:"scatter",
		/*line: {
		  color: '#80CAF6',
		  shape: 'linear'
		},*/
		
		name: res[1]
	  };

    var output_data = [trace1];

    var layout = {
      title: 'velocidade linear em função de número de amostras',
      height: 500, // os valores são todos em pixels
      font: {
      family: 'Lato',
      size: 16,
      color: 'black'
      },

      xaxis: {
            title: 'Amostra[N]',
            titlefont:{
                  color: 'black',
                  size: 14
                  },
                 howticklabels: false
                 // rangemode: 'tozero'
                
                 //rangeslider: {}
            },
      yaxis: {
            title: 'velocidade linear[m/s]',
            fixedrange: true,
            titlefont:{
                  color: 'black',
                  size: 14
                  }
                 // rangemode: 'tozero'
            }
     };

     Plotly.newPlot('myplot', output_data, layout);
   
}



function myStopFunction() {
  clearInterval(Results);
  console.log(Results);
}



///////////////////

function buildPlot2(res) {
  console.log(res);
  var trace2 = {
    // no histograma so é x ou é y.
		x: [],
		//y: [],
    name:'Histograma de Periodo de movimento',
    visible: true,
   // mode: 'lines+markers',
    type: 'histogram',
    xbins: {

      end: 1000, 
  
      size: 0.06, 
  
      start: .5
  
    },
		line: {
		  color: '#80CAF6',
		  shape: 'linear'
		},
    opacity:0.5,
		
		name: res[2]
	  };

    var output_data = [trace2];

    var layout = {
      title: 'Histograma de Periodo de movimento',
      height: 500, // os valores são todos em pixels
      bargap: 0.05, 
  bargroupgap: 0.2,
     
      font: {
      family: 'Lato',
      size: 16,
      color: 'black'
      },

      xaxis: {
            
            title: 'periodo[s]',
            titlefont:{
                  color: 'black',
                  size: 14
                  }
                //  rangemode: 'tozero'
            },
      yaxis: {
        //range:[0.19,0.21],
            title: '# de Eventos',
            titlefont:{
                  color: 'black',
                  size: 14
                  }
                 // rangemode: 'tozero'
            }
     };

     Plotly.newPlot('myplot1', output_data, layout);
   
}


function buildPlot3(res) {
  console.log(res);
  var trace3 = {
		x: [],
		y: [],
    error_y: {
      type: 'data',
      color: '#85144B',
      array: [],
      thickness: 1.5,
      width:3,
      visible: true
    },
    mode: 'lines+markers',
    line: {
      color: "#1f77b4", 
      width: 1
    },marker: {
      color: "rgb(0, 255, 255)", 
      size: 6, 
      line: {
        color: "black", 
        width: 0.5
      }
    },
    type:"scatter",
		
		name: res[3]
	  };

    var output_data = [trace3];

    var layout = {
      title: 'Periodo em função do número de amostras',
      height: 500, // os valores são todos em pixels
      font: {
      family: 'Lato',
      size: 16,
      color: 'black'
      },

      xaxis: {
            
            title: 'Amostra[N]',
            titlefont:{
                  color: 'black',
                  size: 14
                  }
                //  rangemode: 'tozero'
            },
      yaxis: {
        //range:[0.19,0.21],
            title: 'Periodo[s]',
            titlefont:{
                  color: 'black',
                  size: 14
                  }
                  //rangemode: 'tozero'
            }
     };

     Plotly.newPlot('myplot2', output_data, layout);
   
    }
    

// ga
    var gauge_temp = new Gauge({
        renderTo    : 'gauge1',
        width       : 300,
        height      : 300,
        glow        : true,
        units       : '°C',
        valueFormat : { int : 2, dec : 0 },
        title       : "Temperature",
        minValue    : -30,
        maxValue    : 50,
        majorTicks  : ['-30','-20','-10','0','10','20','30','40','50'],
        minorTicks  : 10,
        strokeTicks : false,
        highlights  : [
            { from : -30,   to : -20, color : 'rgba(0, 0, 255, 1)' },
            { from : -20,   to : -10, color : 'rgba(0, 0, 255, .5)' },
            { from : -10, to : 0, color : 'rgba(0, 0, 255, .25)' },
            { from : 0,   to : 10, color : 'rgba(0, 255, 0, .1)' },
            { from : 10, to : 20, color : 'rgba(0, 255, 0, .25)' },
            { from : 20, to : 30, color : 'rgba(255, 0,  0, .25)' },
            { from : 30, to : 40, color : 'rgba(255, 0,  0, .5)' },
            { from : 40, to : 50, color : 'rgba(255, 0,  0, 1)' }
        ],
        colors      : {
            plate      : '#fff',
            majorTicks : '#000',
            minorTicks : '#444',
            title      : '#000',
            units      : '#f00',
            numbers    : '#777',
            needle     : { start : 'rgba(240, 128, 128, 1)', end : 'rgba(255, 160, 122, .9)' }
        }
    });



function set_reset() {
  var resetBtn = document.getElementById('delete_conf');
  var location = window.location.href.split('?')[0];
  
    resetBtn.addEventListener('click', function(event) {
    console.log('Reseting values of R or iteration...');
    window.location.href = location;
    });
    }





