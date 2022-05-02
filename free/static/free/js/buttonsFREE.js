let new_execution = JSON.parse(document.getElementById('execution-config').textContent);
//console.log("test 28")
//console.log(new_execution)
if ( Object.keys(new_execution).length  !== 0)
{
  var apparatus = new_execution.apparatus;
  var protocol = new_execution.protocol.id;
  if (new_execution.status === "C" ){
     //$('.menu .item').tab('change tab','configuration');
     toggleDisable();
  }
}
else{
  var apparatus = JSON.parse(document.getElementById('apparatus-id').textContent);
  var protocol = JSON.parse(document.getElementById('protocol-id').textContent);
  console.log("Rossa");
  console.log(apparatus);
  console.log(protocol);
}
let save = 0;
let endpoint = "";
let method_queue = '';
let execution_id = 0;
let Results=0;
var name = ''
var frist=0;
let table = "";

function toggleDisable(){
    //$("#startButton").toggleClass("disabled");
    $("#startButton").removeClass("disabled");

}

function disableButton(){
    //$("#startButton").toggleClass("disabled");
    $("#startButton").addClass("disabled");

}


function save_name(){
    console.log("OUT : test");
    data_send = config
    data_send["name"] =  $("#name-of-exection").val();
    console.log(document.getElementById('csrf_token').textContent)
    // '{"experiment_name": "Pendulo", "config_experiment": {"DeltaX":'+ String(DeltaX)+', "Samples":'+String(Samples)+' }}'
    HEADERS = {
        "X-CSRFToken": document.getElementById('csrf_token').textContent,
        }
    var endpoint="/api/v1/execution/"+new_execution.id+"/name";
    // print out
    console.log('JSON : ' +  endpoint);
    console.log(data_send);
    axios({
        method: 'patch', //you can set what request you want to be
        url: endpoint,
        headers: HEADERS,
        data: data_send,
    }).then(response => {
        console.log('plotly_results', response);
        toggleDisable();
    }).catch(console);
}


function queue(config) {
    if (Object.keys(new_execution).length  !== 0)
    {
      execution_id = new_execution.id
      endpoint="/api/v1/execution/"+new_execution.id;
      method_queue = 'put'
      data_send = new_execution
    }
    else
    {
      endpoint="/api/v1/execution";
      method_queue = 'post';
      data_send = {"apparatus": apparatus, "protocol": protocol}
    }
    // get inputs values from the client side
    config_input.findConfigInput();
    
    data_send["config"] = config.processElements()
    
  
    if ($("#name-of-exection").val() !== undefined){
      name = $("#name-of-exection").val();
      data_send["name"] = name 
    }
    else{
      data_send["name"] = ""
    }
   
  
    // '{"experiment_name": "Pendulo", "config_experiment": {"DeltaX":'+ String(DeltaX)+', "Samples":'+String(Samples)+' }}'
    HEADERS = {
      "X-CSRFToken": document.getElementById('csrf_token').textContent,
      }
    // print out
    console.log('JSON : ' +  endpoint);
    console.log('JSON : ' +  data_send);
  
  
    axios({
      method: method_queue, //you can set what request you want to be
      url: endpoint,
      headers: HEADERS,
      data: data_send,
    }).then(response => {
      if (method_queue === 'post')
      {
        //console.log("http://elab-dev.vps.tecnico.ulisboa.pt:8008/execution/"+String(response.data.id))
        //location.replace("http://elab-dev.vps.tecnico.ulisboa.pt:8008/execution/"+String(response.data.id))
        window.history.pushState("","",'/execution/'+String(response.data.id))
        new_execution = response.data;
      }
      console.log('plotly_results', response);
      toggleDisable();
    }).catch(console);  
  
  }
  
  
  const updateTableRunTime = () => {
    var currentDate = new Date()
    var seconds = currentDate.getSeconds();
      var minutes = currentDate.getMinutes();
      var hour = currentDate.getHours();
      var day = currentDate.getDate()
      var month = currentDate.getMonth() + 1  // starts from zero
      var year = currentDate.getFullYear()
  
     var d = day + "-" + month + "-" + year  + "  " + hour + "_" + minutes + "_" + seconds;
  
  
    // - MESSAGES
    $('.message .close').on('click', function() {
        $(this)
          .closest('.message')
          .transition('fade')
        ;
    });
    // - DATATABLES
    table = $('#table_result_runtime').DataTable({
          lengthChange: false,
          buttons: [ 'copy',
      {
                extend: 'csv',
                title: 'Pendulum_results__' + d  
            },
      {
                extend: 'excel',
                title: 'Pendulum_results__' +d
            },
      
      ]
      });
      table.buttons().container().appendTo(
        $('div.eight.column:eq(0)', table.table().container()) 
      );
  
  }
  
  $(document).ready(function(){
    updateTableRunTime();
  
  });
  
  let html_tabele = document.getElementById("table_result").innerHTML;
  
  const writeLineOnTable = (keys,response) => {
    table.destroy();
    html_tabele += `<tr>`;
    keys.forEach(function(data) 
    {
      
      html_tabele += `<td>` + response.data[0].value[data]  +  `</td>`;
      
      
    });
    html_tabele += `</tr>`;
    document.getElementById("table_result").innerHTML = html_tabele;
    updateTableRunTime();
  }
  
    function myStopFunction() {
        clearInterval(Results);
        console.log(Results);
    }

    function myStartFunction() {
        Results = setInterval(getData,500)
        console.log("Valor da função");
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
            rist = buildGraph(response)
          }
        }
        console.log(response);
        // check for ending of the experiment
        if (response.data.result_type !== 'undefined' && response.data[0].result_type === 'f'){
            //$('#table_result_1').DataTable().ajax.reload();
            myStopFunction();
        }
        else{
          if (typeof response.data[0] === 'object'){
            plotRunTime(response)
            keys  = Object.keys(response.data[0].value);
            
            writeLineOnTable(keys,response)
    
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

  
  function start() {
    execution_id = new_execution.id;
    var endpoint_2="/api/v1/execution/"+execution_id+"/start";
    console.log('JSON : ' +  endpoint_2);
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
  
