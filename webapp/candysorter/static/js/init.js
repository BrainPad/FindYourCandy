$(function () {

	// APIの設定
	var pid = Math.floor(Math.random() * 10000000000000000); // ポストするID
	var morUrl = "/api/morphs"; // 形態素解析のPOST先
	var simUrl = "/api/similarities"; // 類似度のPOST先
	var pickUrl = "/api/pickup"; // お菓子ピックアップのPOST先

	// 変数の用意
	var speechTxt = "I like chewy chocolate candy"; // 入力文字列の保存
	var sim = ""; // 推論データの保存
	var nlFlg = false; // NLの表示進行状況
	var simFlg = false; // 推論データの取得状況
	var winW = window.innerWidth;
	var winH = window.innerHeight;

	// 推論データの監視
	var simTimer = setInterval(function () {
		if (nlFlg == true && simFlg == false && sim != "") {
			simFlg = true;
			clearInterval(simTimer);
			force();
			plot();
		}
	}, 100);

	// 音声認識の処理
	var speech = function () {
		$("body").addClass("mode-speech-start");
		var recognition = new webkitSpeechRecognition();
		recognition.lang = "en";
		$(".speech-mic").click(function () {
			$("body").addClass("mode-speech-in");
			recognition.start();
		});
		recognition.onerror = function () {
			$("body").removeClass("mode-speech-in");
		};
		recognition.onresult = function (e) {
			speechTxt = e.results[0][0].transcript
			$(".speech-out").text(speechTxt);
			$("body").addClass("mode-speech-out");
			setTimeout(nl, 1500);
		};
	}

	// NLの処理
	var nl = function () {
		$.ajax({
			type: "POST",
			contentType: "application/json",
			dataType: "json",
			url: morUrl,
			data: JSON.stringify({
				"id": pid,
				"text": speechTxt
			}),
			error: function (textStatus) {
				console.log(textStatus);
			},
			success: function (data) {
				// 形態素の生成
				data = data.morphs
				for (var i in data) {
					var morph = "";
					for (key in data[i].pos) {
						var txt = data[i].pos[key];
						if (key != "tag" && txt.indexOf("UNKNOWN") == -1) {
							morph += key + "=" + txt + "<br>";
						}
					}
					var desc = "<dl>";
					desc += "<dd class='nl-label'>" + data[i].depend.label + "</dd>";
					desc += "<dd class='nl-word'>" + data[i].word + "</dd>";
					desc += "<dd class='nl-tag'>" + data[i].pos.tag + "</dd>";
					desc += "<dd class='nl-pos'>" + morph + "</dd>";
					desc += "</dl>"
					$(".nl-syntax").append(desc);
					// 矢印の生成
					for (var j in data[i].depend.index) {
						$(".nl-depend").append("<dd data-from=" + i + " data-to=" + data[i].depend.index[j] + "></dd>");
					}
				}
				// X座標の計測
				var dependX = [];
				$(".nl-syntax dl").each(function (index) {
					var x = $(".nl-syntax dl:nth-child(" + (index + 1) + ")").position().left;
					var w = $(".nl-syntax dl:nth-child(" + (index + 1) + ")").outerWidth();
					dependX.push(Math.round(x + w / 2));
				});
				// 矢印の再配置
				$(".nl-depend dd").each(function (index) {
					var from = $(this).data().from;
					var to = $(this).data().to;
					if (from < to) {
						var x = dependX[from];
						var w = dependX[to] - dependX[from];
					} else {
						var x = dependX[to];
						var w = dependX[from] - dependX[to];
						$(this).addClass("left");
					}
					$(this).css({
						top: (Math.abs(from - to) - 1) * -30 + "px",
						left: x + "px",
						width: w + "px"
					});
				});
				// エフェクトの設定
				$(".nl-word").each(function (index) {
					$(this).css("transition-delay", index / 10 + "s");
				});
				$(".nl-tag, .nl-pos").each(function (index) {
					$(this).css("transition-delay", 1 + index / 20 + "s");
				});
				$(".nl-label, .nl-depend dd").css("transition-delay", 2 + "s");
				$("body").addClass("mode-nl-loaded");
				setTimeout(function () {
					nlFlg = true;
				}, 3000);
			}
		});
		// 推論データの取得
		$.ajax({
			type: "POST",
			contentType: "application/json",
			dataType: "json",
			url: simUrl,
			data: JSON.stringify({
				"id": pid,
				"text": speechTxt
			}),
			error: function (textStatus) {
				console.log(textStatus);
			},
			success: function (data) {
				sim = data;
			}
		});
	};

	// フォースレイアウトの描画
	var force = function () {
		$("body").addClass("mode-force-start");
		// 読み込みデータからデータセットを作成
		var data = sim.similarities.force;
		var dataSet = {
			"nodes": [],
			"links": []
		};
		for (var i in data) {
			dataSet.nodes.push(data[i]);
			dataSet.links.push({
				"source": 0,
				"target": parseInt(i) + 1
			});
		}
		// データセットの先頭に入力文字列用のノードを追加
		dataSet.nodes.unshift({
			"label": "",
			"lid": 0,
			"em": 0,
			"x": winW / 2,
			"y": winH / 2,
			"fixed": true
		});
		// SVGを作成
		var svg = d3.select(".force").append("svg").attr({
			width: winW,
			height: winH
		});
		// レイアウトの設定
		var d3force = d3.layout.force()
			.nodes(dataSet.nodes)
			.links(dataSet.links)
			.size([winW, winH])
			.linkDistance(250)
			.charge(-1000)
			.start();
		var link = svg.selectAll("line")
			.data(dataSet.links)
			.enter()
			.append("line");
		var g = svg.selectAll("g")
			.data(dataSet.nodes)
			.enter()
			.append("g")
			.attr("class", function (d) {
				return "label-" + d.lid;
			});
		var circle = g.append("circle")
			.attr("r", function (d) {
				var r = 50 + d.em * 100;
				return r;
			});
		var label = g.append("text")
			.text(function (d) {
				return d.label;
			});
		// 座標の設定（入力文字列（lid=0）は画面中央に固定）
		d3force.on("tick", function () {
			g.attr("transform", function (d) {
				return "translate(" + d.x + "," + d.y + ")";
			});
			link.attr("x1", function (d) {
					return d.source.x;
				})
				.attr("y1", function (d) {
					return d.source.y;
				})
				.attr("x2", function (d) {
					return d.target.x;
				})
				.attr("y2", function (d) {
					return d.target.y;
				});
		});
		// 画面中央に入力文字列を配置
		$(".force").prepend("<div class='force-txt'>" + speechTxt + "<div>");
		var txtW = $(".force-txt").outerWidth();
		var txtH = $(".force-txt").outerHeight();
		$(".force-txt").css({
			top: (winH - txtH) / 2 + "px",
			left: (winW - txtW) / 2 + "px"
		});
	};

	// 散布図の描画
	var plot = function () {
		// 読み込みデータからデータセットを作成
		var data = sim.similarities.embedded;
    console.log(data);
		var dataSet = [];
		for (var i in data) {
			var em = 0; // 類似度の高いラベルを抽出
			var lid = 0;
			for (var j in data[i].similarities) {
				if (data[i].similarities[j].em > em) {
					lid = data[i].similarities[j].lid;
					em = data[i].similarities[j].em;
				}
			}
			dataSet.push({
				"x": data[i].coords[0] * winW,
				"y": data[i].coords[1] * winH,
				"img": data[i].url,
				"lid": lid
			});
		}
		// データセットの最後にnearestを追加
		data = sim.similarities.nearest;
		em = 0; // 類似度の高いラベルを抽出
		lid = 0;
		for (var i in data.similarities) {
			if (data.similarities[i].em > em) {
				lid = data.similarities[i].lid;
				em = data.similarities[i].em;
			}
		}
		dataSet.push({
			"x": data.coords[0] * winW,
			"y": data.coords[1] * winH,
			"img": data.url,
			"lid": lid
		});
		$(".cam polygon").addClass("label-" + lid);
		// 散布図の描画
		for (var i in dataSet) {
			$(".plot").append("<dd><i></i></dd>");
			$(".plot dd:last-child").addClass("label-" + dataSet[i].lid)
				.css({
					left: dataSet[i].x + "px",
					top: dataSet[i].y + "px",
					transitionDelay: parseInt(i) * 0.03 + "s"
				});
			$(".plot dd:last-child i")
				.css({
					backgroundImage: "url(" + dataSet[i].img + ")"
				});
		}
		$(".plot dd:last-child").addClass("nearest");
		// 時間差で描画
		setTimeout(function () {
			$("body").addClass("mode-plot-start");
		}, 1000);
		setTimeout(function () {
			$("body").addClass("mode-plot-end");
			cam();
		}, 5000);
	};

	// カメラ画像の出力
	var cam = function () {
		var imgUrl = sim.similarities.url;
		// 画像サイズの取得
		var img = new Image();
		img.src = imgUrl;
		img.onload = function () {
			var w = img.width;
			var h = img.height;
			$(".cam-img svg").attr("viewBox", "0 0 " + w + " " + h);
			if (w > winW) {
				h = h / w * winW;
				w = winW;
			}
			if (h > winH) {
				w = w / h * winH;
				h = winH;
			}
			$(".cam-img").width(w).height(h);
		};
		// 画像の設定
		$(".cam-img").css("background-image", "url(" + imgUrl + ")");
		var box = sim.similarities.nearest.box;
		$(".cam polygon").attr("points", box[0][0] + "," + box[0][1] + " " + box[1][0] + "," + box[1][1] + " " + box[2][0] + "," + box[2][1] + " " + box[3][0] + "," + box[3][1] + " ");
		// 時間差で描画
		setTimeout(function () {
			$("body").addClass("mode-cam-start");
		}, 2000);
		setTimeout(function () {
			thanks();
		}, 9000);
		// ピックアップの操作
		$.ajax({
			type: "POST",
			contentType: "application/json",
			dataType: "json",
			url: pickUrl,
			data: JSON.stringify({
				"id": pid
			}),
			error: function (textStatus) {
				console.log(textStatus);
			},
			success: function (data) {
				sim = data;
			}
		});
	};

	// エンドロールの描画
	var thanks = function () {
		$("body").addClass("mode-thanks-start");
		setTimeout(function () {
			$("body").addClass("mode-thanks-end");
		}, 3000);
	};

	// 処理の開始
	//$.getJSON(simUrl, function (data) {
	//	sim = data;
	//	cam();
	//	orce();
	//	plot();
	//});
	speech();
});
