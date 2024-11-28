$(document).ready(function () {
    let led_state;
    let motor_state;
      getFanState();  // Call the function to set the initial fan opacit
      setInterval(getFanState, 3000);

    function getFanState() {
        fetch("/get_motor_state")
            .then((response) => response.json())
            .then((data) => {
              console.log("Motor state FETCHED: ", data.motor_status);
                motor_state = data.motor_status;
                console.log("Motor state received:", data);
                $("#fan").css("opacity", motor_state ? "1" : "0.3");  // Update opacity after motor state is updated
            })
            .catch((error) => {
                console.error("Error fetching motor state:", error);
            });
    }

    $("#fan").click(function () {
        const url = motor_state ? "/stop_motor" : "/start_motor";
        console.log("URI CALLED: ", url);
        console.log("BECAUSE motor_stae = ",motor_state );
        
        fetch(url)
            .then((response) => response.json())
            .then((data) => {
              console.log("Motor state changed to: ", data.status);
                motor_state = data.status;
                $("#fan").css("opacity", motor_state ? "1" : "0.3");  // Update opacity based on new motor state
            })
            .catch((error) => {
                console.error("Error toggling motor state:", error);
            });
    })

    function setHumidityValue(humidityValue) {
      if (humidityValue === "") {
        $(".circle-inner, .gauge-copy").css({
          transform: "rotate(-45deg)",
        });
        $(".gauge-copy").css({
          transform: "translate(-50%, -50%) rotate(0deg)",
        });
        $(".percentage").text("0 %");
      } else if (humidityValue >= 0 && humidityValue <= 100) {
        var newVal = humidityValue * 1.8 - 45;
        $(".circle-inner, .gauge-copy").css({
          transform: "rotate(" + newVal + "deg)",
        });
        $(".gauge-copy").css({
          transform:
            "translate(-50%, -50%) rotate(" + humidityValue * 1.8 + "deg)",
        });
        $(".percentage").text(humidityValue + " %");
      } else {
        $(".percentage").text("Invalid input value");
      }
    }

    const config = {
      minTemp: -20,
      maxTemp: 50,
    };

    // Change temperature

    const range = document.querySelector("input[type='range']");
    const temperature = document.getElementById("temperature");

    function setTemperature(temp) {
      temperature.style.height =
        ((temp - config.minTemp) / (config.maxTemp - config.minTemp)) * 100 +
        "%";
      temperature.dataset.value = temp + "°C";
    }

    // setTimeout(setTemperature, 1000);
    

    function getLedState() {
      fetch("/get_led_state")
        .then((response) => response.json())
        .then((data) => {
          led_state = data.led_state;
          setImages();
        })
        .catch((e) => console.log("Error", e));
    }

    setInterval(getLedState, 1000);

    $("#switch").click(function () {
      fetch("/switch_led")
        .then((response) => response.json())
        .then((data) => {
          led_state = data.led_state;
          console.log(data);
          setImages();
        })
        .catch((e) => console.error("Error:", e));
    });

    function updateTempHumidity() {
      fetch("/get_temp_humidity")
        .then((response) => response.json())
        .then((data) => {
          console.log("Data received:", data);
          setTemperature(data.temperature);
          setHumidityValue(data.humidity);
        })
        .catch((error) => {
          console.error("Error fetching data:", error);
        });
    }

    updateTempHumidity();

    setInterval(updateTempHumidity, 5000);

    function setImages() {
      $("#switch").attr("src", `../static/images/switch_${led_state}.png`);
      $("#light").attr("src", `../static/images/light_${led_state}.png`);
    }

    function updateLightData() {
      fetch("/get_light_data")
        .then((response) => response.json())
        .then((data) => {
          const lightIntensity = data.light_intensity;
          const lightStatus = data.light_status;
    
          $("#light-fill").css("width", `${lightIntensity}%`);
          $("#light-value").text(`${lightIntensity}%`);
          $("#light-status").text(lightStatus ? "ON" : "OFF");
    
          if (lightStatus && data.email_sent) {
            $("#email-notification").show().text("Email has been sent.");
          } else {
            $("#email-notification").hide();
          }
        })
        .catch((error) => console.error("Error fetching light data:", error));
    }
    
    setInterval(updateLightData, 3000);
    
  });