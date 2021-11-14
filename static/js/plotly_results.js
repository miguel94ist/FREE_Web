/* Javascript used to start an experiment and showns graphics in real time

Developed by José Veiga and Pedro Rosa

Last updated out 9 11:12 , 2021*/


// starting all the variables
var base_url = "http://10.2.12.86:8000";

result_data = JSON.parse(document.getElementById('final-result').textContent);
var apparatus = JSON.parse(document.getElementById('execution-config').textContent).apparatus;
var protocol = JSON.parse(document.getElementById('execution-config').textContent).protocol.id;
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
let save_table = ""

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

$(".menu .item").click(function() {
  var tab_description = $(this).attr("data-tab");
  // console.log('Description : ', tab_description);
  if (tab_description === 'results')
  {
    Show_data()
  }
  });

function Show_data(){
  result_data = JSON.parse(document.getElementById('final-result').textContent);
  buildPlot1(0);
  buildPlot2(0);
  buildPlot3(0);
  receive_error_velocity = 0.1;
  receive_error_period = 0.0005;//response.data.value.e_period;
  Plotly.extendTraces('myplot', {x: [result_data.value.map(data => data.Sample_number)],y: [result_data.value.map(data => data.Val3)],'error_y.array': [Array(result_data.value.length).fill(receive_error_velocity)]}, [0]);
  Plotly.extendTraces('myplot1', {x:  [result_data.value.map(data => data.Val1)]}, [0]);
  Plotly.extendTraces('myplot2', {x: [result_data.value.map(data => data.Sample_number)],y: [result_data.value.map(data => data.Val1)],'error_y.array': [Array(result_data.value.length).fill(receive_error_period)]}, [0]);


}


// This function receive as input the parameters and send them to the experiment and send back the data to browser*/

function queue() {
  // get inputs values from the client side
  if ($("#DeltaX").val() !== undefined)
    DeltaX = $("#DeltaX").val();
  if ($("#Samples").val() !== undefined)
    Samples = $("#Samples").val();

  
  data_send = {"apparatus": apparatus, "protocol": protocol, "config": {"deltaX": parseInt (DeltaX), "samples":parseInt (Samples)}}
  // '{"experiment_name": "Pendulo", "config_experiment": {"DeltaX":'+ String(DeltaX)+', "Samples":'+String(Samples)+' }}'
  HEADERS = {
    "X-CSRFToken": getCookie("csrftoken"),
    }
  var endpoint="/api/v1/execution";
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


function myStopFunction() {
  clearInterval(Results);
  console.log(Results);
}

let last_result_id =0 
// Receive data from experiment
function getData(){
  let endpoint_result =  "/api/v1/execution/"+execution_id+"/result/0";
  if (frist === 0)
  {
    endpoint_result = "/api/v1/execution/"+execution_id+"/result/0";
  }
  else{
    endpoint_result = "/api/v1/execution/"+execution_id+"/result/"+last_result_id
  }

  axios({
    method: 'get', //you can set what request you want to be
    url: endpoint_result,
    headers: HEADERS,
  }).then(response => {
    console.log('plotly_results', response.data);
    if (frist === 0)
    {
      if (response.data !== "")
      {
        console.log('ola', response.data[0].value);
        res = Object.keys(response.data[0].value);
        buildPlot1(res);
        buildPlot2(res);  // grafico de temperatura não 
        buildPlot3(res);
        last_result_id = response.data[0].id+1
        frist = 1;
      }
    }
    console.log(response);
    // check for ending of the experiment
    if (response.data.result_type !== 'undefined' && response.data[0].result_type === 'f'){
        myStopFunction();
    }
    else{
      if (typeof response.data[0] === 'object'){
        console.log('plotly_results', response.data.value);
        
        receive_error_velocity = 0.1;
        receive_error_period = 0.0005;//response.data.value.e_period;
        
        Plotly.extendTraces('myplot', {x: [[response.data[0].value.Sample_number]],y: [[response.data[0].value.Val3]],
          'error_y.array': [[ receive_error_velocity ]]}, [0]);
        last_result_id = response.data[0].id+1
        Plotly.extendTraces('myplot1', {x: [[response.data[0].value.Val1]]}, [0]);
        Plotly.extendTraces('myplot2', {x: [[response.data[0].value.Sample_number]],y: [[response.data[0].value.Val1]],
        'error_y.array': [[receive_error_period]]}, [0]);
  

      html = save_table
      // console.log("ola",save_table) 
      keys  = Object.keys(response.data[0].value);
      html += "<tr>";
      keys.forEach(function(data) 
      {
        // console.log("pppp ",data)
        
        html += "<td>" + response.data[0].value[data]  +  "</td>";
        
        
      });
      html += "</tr>";
      save_table = html
  // assumes <div id="result"></div>
         document.getElementById("table_result").innerHTML = html;
        //  console.log("coisas html table ",html);
      }
      // getData();
    }
   
  }).catch(error => {
    if (error.response !== undefined) {
    console.error('Error : ', error.response.data);
    }
  });
  
}

function myStartFunction() {
  Results = setInterval(getData,500)
  console.log("Valor da função");
  console.log(Results);
}


function start() {
  var endpoint_2="/api/v1/execution/"+execution_id+"/start";
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
  myStartFunction();
}





//// nao usado
function tablebind(response) {  
          if (obj.length > 0) {  

              var table = $("<table />");  
              table[0].border = "1";  

              var row$;  

              var columns = addAllColumnHeaders(["S"]);  
              for (var i = 0; i < data.length; i++)
               {  
                  row$ = $('<tr/>');  
           
                  for (var colIndex = 0; colIndex < columns.length; colIndex++) 
                  {  
                      var cellValue = data[i][columns[colIndex]];  

                      if (cellValue == null) { cellValue = ""; }  

                      row$.append($('<td/>').html(cellValue));  
                  }  
                  $("#jsonTable").append(row$);  
              }      
          }  

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
    nbins: 50,
    // xbins: {

    //   end: 1000, 
  
    //   size: 0.06, 
  
    //   start: .5
  
    // },
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
    




function set_reset() {
  var resetBtn = document.getElementById('delete_conf');
  var location = window.location.href.split('?')[0];
  
    resetBtn.addEventListener('click', function(event) {
    console.log('Reseting values of R or iteration...');
    window.location.href = location;
    });
    }





