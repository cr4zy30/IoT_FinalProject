$(document).ready(function () {
    let led_state;

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

    fetch("/get_led_state")
      .then((response) => response.json())
      .then((data) => {
        led_state = data.led_state;
        setImages();
      })
      .catch((e) => console.log("Error", e));

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
  });