$(function () {

	// API settings
	var pid = Math.floor(Math.random() * 10000000000000000); // POST ID
	var capUrl = "/api/capture"; // API for caputure
	var trainUrl = "/api/train"; // API for learning
	var statUrl = "/api/status"; // API for status check
	var statFirst = 15000; // wait time to read initial learning status (ms)
	var statInterval = 10000; // reading interval of Learning status (ms)
	var lossMax = 1800; // estimated number of loss value
	var statTest = 0; // dummy variable for test（dev：1、prd：0）
	var loadSec = 2000; //　Time lag for loading screen test (return to 0 in prd environment)

	// variables
	var stepFlg = 0; // capture step
	var capDat = []; // save capture data
	var winW = window.innerWidth;
	var winH = window.innerHeight;

	// language setting
	var lang = window.sessionStorage.getItem("lang");
	if (lang === null) {
		lang = "en";
		window.sessionStorage.setItem("lang", lang);
	}

	// switch language
	$("body").addClass("mode-" + lang);
	$(".cap-lang a").click(function () {
		$("body").removeClass("mode-en mode-ja");
		if ($(this).text() == "EN") {
			$(this).text("JP");
			lang = "ja";
		} else {
			$(this).text("EN");
			lang = "en";
		}
		window.sessionStorage.setItem("lang", lang);
		$("body").addClass("mode-" + lang);
		return false;
	});

	// processing capture mode
	var cap = function () {
		$("body").addClass("mode-cap-init");
		$(".cap-lang a").text(lang == "en" ? "EN": "JP");
	};
	$(".cap-start, .cap-retry").click(function () {
		$("body").addClass("mode-loading");
		if ($(this).hasClass("cap-start")) {
			stepFlg += 1;
		};
		$.ajax({
			type: "POST",
			contentType: "application/json",
			dataType: "json",
			url: capUrl,
			data: JSON.stringify({
				"id": pid,
				"step": stepFlg
			}),
			error: function (textStatus) {
				console.log(textStatus);
				sorry();
			},
			success: function (data) {
				// difference time for debug
				setTimeout(function () {
					$("body").addClass("mode-cap-steps");
					$(".cap-labels").html("");
					$(".cap-images").html("");
					for (var i in data.labels) {
						$(".cap-labels").append("<dd>" + data.labels[i] + "</dd>");
					}
					for (var i in data.urls) {
						$(".cap-images").append("<dd style='background-image:url(" + data.urls[i] + ")'></dd>");
						$(".cap-images dd:last-child").css("animation-delay", parseInt(i) / 10 + "s");
						$(".cap-step").text(stepFlg);
						capDat.push(data.urls[i]);
					}
					if (stepFlg == 4) {
						$(".cap-start").parent().hide();
						$(".cap-done").parent().show();
					} else {
						$(".cap-start").parent().show();
						$(".cap-done").parent().hide();
					}
					$("body").removeClass("mode-loading");
				}, loadSec);
			}
		});
		return false;
	});

	// start learning
	var trainStarted = false;
	var train = function () {
		$("body").addClass("mode-train");
		// start request
		$.ajax({
			type: "POST",
			contentType: "application/json",
			dataType: "json",
			url: trainUrl,
			data: JSON.stringify({
				"id": pid
			}),
			error: function (textStatus) {
				console.log(textStatus);
				clearInterval(statTimer);
				sorry();
			},
			success: function (data) {
				trainStarted = true;
			}
		});
		// draw package images
		for (var i = 0; i < capDat.length; i++) {
			$(".train-images").append("<dd style='background-image:url(" + capDat[i] + ")'></dd>");
			$(".train-images dd:last-child").css({
				top: winH / 2,
				left: winW / 2,
				transitionDelay: i / 10 + "s"
			});
		}
		// Pending processing effect
		var waiting = capDat.length * 100 + 2000;
		setTimeout(function () {
			$(".train-images dd").each(function () {
				var x = Math.floor(Math.random() * (winW / 2 - (winW / -2)) + (winW / -2));
				var y = Math.floor(Math.random() * (winH / 2 - (winH / -2)) + (winH / -2));
				$(this).css({
					opacity: 0,
					transform: "scale(1) translate(" + x + "px," + y + "px)"
				});
			});
		}, 1000);
		setTimeout(function () {
			$("body").addClass("mode-train-v3");
		}, waiting);
		stat();
	};
	$(".cap-done").click(function () {
		train();
		return false;
	});

	// POST processing
	var runFlg = false; // status
	var compFlg = false; // status
	var statTimer = setInterval(function () {}, 100);
	var statPost = function () {
		if (!trainStarted) {
			return;
		}
		if (compFlg) {
			clearInterval(statTimer);
		} else {
			// for test
			if (statTest > 0) {
				if (statTest > 1) {
					statUrl = "/api/status-test" + statTest + ".json" + "?_=" + pid;
				}
				statTest += 1;
			}
			$.ajax({
				type: "POST",
				contentType: "application/json",
				dataType: "json",
				url: statUrl,
				data: JSON.stringify({
					"id": pid
				}),
				error: function (textStatus) {
					console.log(textStatus);
					clearInterval(statTimer);
					sorry();
				},
				success: function (data) {
					if (data.status == "preparing") {
						return;
					}
					if (data.status == "canceled") {
						compFlg = true;
						sorry();
						return;
					}
					if (data.status == "failed") {
						compFlg = true;
						sorry();
						return;
					}
					if (data.status == "running" || data.status == "complete") {
						if (!runFlg) {
							$("body").addClass("mode-stat");
							runFlg = true;
						}
						if (data.status == "complete") {
							compFlg = true;
						}
					}
					lossDat = data.loss;
					statLoss();
					plot(data.embedded);
				}
			});
		}
	}
	var stat = function () {
		statPost();
		statTimer = setInterval(statPost, statInterval);
	};

	// draw process of Loss
	var lossDat = [];
	var lossStep = 0;
	var lossW = winW - 200;
	var lossH = winH / 2;
	var lossY = lossW / lossMax;
	var lossInterval = 0;
	var lossSvg = d3.select(".stat-loss").append("svg").attr("width", lossW).attr("height", lossH);
	var lossTimer = setInterval(function () {}, 100);
	var statLoss = function () {
		$(".stat-loss").width(lossW);
		if (compFlg) {
			lossInterval = 10; // The last is 10 ms interval
		} else {
			lossInterval = Math.ceil(statInterval / (lossDat.length - lossStep));
		}
		clearInterval(lossTimer);
		lossTimer = setInterval(function () {
			if (lossStep < lossDat.length - 1) {
				if (lossW < (lossStep + 1) * lossY) {
					lossSvg.attr("width", (lossStep + 1) * lossY);
				}
				lossSvg.append("line")
					.attr("x1", lossStep * lossY)
					.attr("y1", lossH - lossDat[lossStep] * lossH)
					.attr("x2", (lossStep + 1) * lossY)
					.attr("y2", lossH - lossDat[lossStep + 1] * lossH);
				lossStep += 1;
				$(".stat-loss-x").text(lossStep + 1);
				$(".stat-loss-y").text((lossDat[lossStep]).toFixed(3));
			} else if (compFlg) {
				$("body").addClass("mode-stat-end");
			}
		}, lossInterval);
	};

	// draw scatter plot
	var plot = function (data) {
		$("body").removeClass("mode-plot-start");
		$(".plot, .plot-label").html("");
		var label = [];
		for (var i in data) {
			$(".plot").append("<dd><i></i></dd>");
			$(".plot dd:last-child").addClass("label-" + data[i].property.lid)
				.css({
					left: data[i].coords[0] * lossW + "px",
					top: data[i].coords[1] * lossH + "px",
					transitionDelay: parseInt(i) * 0.05 + "s",
					animationDelay: parseInt(i) * 0.05 + "s"
				});
			$(".plot dd:last-child i")
				.css({
					backgroundImage: "url(" + data[i].url + ")"
				});
			label[data[i].property.lid] = data[i].property.label; // generate label array
		}
		for (var i in label) {
			$(".plot-label").append("<dd class=label-" + i + ">" + label[i] + "</dd>");
		}
		// draw with different time
		setTimeout(function () {
			$("body").addClass("mode-plot-start");
		}, 100);
	};

	// draw sorry
	var sorry = function () {
		$("body").addClass("mode-sorry-t-start");
		setTimeout(function () {
			$("body").addClass("mode-sorry-t-end");
		}, 300);
	};

	cap();
});
