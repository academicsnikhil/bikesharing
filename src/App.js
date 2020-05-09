import React, { useState, useEffect } from 'react';
import './App.css';

function App() {

  const formatDate = function(date){
    var year = '' + new Date().getFullYear();
    var month = '' + (new Date().getMonth() + 1);
    var day = '' + new Date().getDate();
    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;
    console.log("month ",month,"day ", day);
    return [year, month, day].join('-');
}

const formatTime = function(){
  var hour = '' + new Date().getHours();
  var minutes = '' + new Date().getMinutes();
  if (hour.length < 2) 
      hour = '0' + hour;
  if (minutes.length < 2) 
      minutes = '0' + minutes;
  return [hour, minutes].join(':');
}
  const date = formatDate(new Date().getFullYear() + '-' + new Date().getMonth()+ '-' + new Date().getDate());
  const time = formatTime();
  const [stations, setStations] = useState(0);
  const [demand, setDemand] = useState(0);
  const [selectedOption, setSelectedOption] = useState(0);
  const [selectedDate, setSelectedDate] = useState(date);
  const [selectedTime, setSelectedTime] = useState(time);
  function getDemand(e){
    if(selectedOption !== 0 && selectedTime !== 0 && setSelectedDate !== 0){
      const input_stream = {"station_name" : selectedOption, "date" : selectedDate, "time" : selectedTime} 
      fetch('/get_demand' + '?' + JSON.stringify(input_stream)).then(res => res.json()).then(demand => {
        setDemand(demand);
      });
    }
  }
  const getKeys = function () {
    const keys = Object.keys({'station_id' :'zero', 'station_name' : 'one',  'demand' : 'two', 'availability' : 'three'})
    return keys
  }
  const getHeader = function () {
    const keys = stations && getKeys();
    return keys.map((key, index) => {
      return <th key={key}>{key.toUpperCase()}</th>
    })
  }
  const RenderRow = (props) => {
    return props.keys.map((key, index) => {
      return <td key={props.data[key]}>{props.data[key]}</td>
    })
  }

  const getRowsData = function () {
    const keys = stations && getKeys();
    return stations.map((row, index) => {
      return <tr key={index}>{<RenderRow key={index} data={row} keys={keys} />}</tr>
    })
  }
  const getDemandKeys = function () {
    const keys = Object.keys({'station_id' :'zero', 'station_name' : 'one',  'demand' : 'two', 'availability' : 'three'})
    return keys
  }
  const getDemandHeader = function () {
    const keys = demand && getDemandKeys();
    return keys.map((key, index) => {
      return <th key={key}>{key.toUpperCase()}</th>
    })
  }
  const RenderDemandRow = (props) => {
    return props.keys.map((key, index) => {
      return <td key={props.data[key]}>{props.data[key]}</td>
    })
  }

  const getDemandRowsData = function () {
    const keys = demand && getDemandKeys();
    return demand.map((row, index) => {
      return <tr key={index}>{<RenderDemandRow key={index} data={row} keys={keys} />}</tr>
    })
  }


  useEffect(() => {
    fetch('/home').then(res => res.json()).then(stations => {
      setStations(stations);
      setSelectedDate(date);
      console.log(time);
      setSelectedTime(time);
    });
  }, []);
  return (

    <div className="App">
      <header className="App-header">
        <h2>Capital Bike Sharing - Hourly Demand Prediction</h2>
      </header>
      <div className="station-form">
        <div className="station-name">
          <label for="stations">Station name</label>
          <br />
          <select onChange={e=> setSelectedOption(e.target.value)}>
            <option default>Select station</option>
            {stations && stations.map((station) =>
            <option key={station.station_id} value={station.station_name}>{station.station_name}</option>)}
          </select>
        </div>
        <div className="date">
          <label for="date">Date</label>
          <br />
          <input  defaultValue={date} onChange={e=> setSelectedDate(e.target.value)} type="date" id="date" name="date" />
        </div>
        <div className="time">
          <label for="time">Time</label>
          <br />
          <input defaultValue={time} onChange={e=> setSelectedTime(e.target.value)} type="time" id="time" name="time" />
        </div>
        <div>
          <button onClick = {getDemand}> Get Demand</button>
        </div>
      </div>
      <div>
      { demand ? 
      <div>
        <table className="demand_table">
          <thead>
            <tr>{demand && getDemandHeader()}</tr>
          </thead>
           <tbody>
            {demand && getDemandRowsData()}
          </tbody>
        </table>
      </div>
      :
      <div>
      <table className="stations_table">
      <thead>
        <tr>{stations && getHeader()}</tr>
      </thead>
       <tbody>
        {stations && getRowsData()}
      </tbody>
    </table>
  </div> }
  </div>
  </div>
  );
}

export default App;
