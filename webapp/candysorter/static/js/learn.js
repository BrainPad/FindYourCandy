$(function () {

	// APIの設定
	var pid = Math.floor(Math.random() * 10000000000000000); // ポストするID
	var capUrl = "/api/capture"; // 撮影のPOST先
	var trainUrl = "/api/train"; // 学習スタートのPOST先
	var statUrl = "/api/status"; // 進捗確認のPOST先
	var statFirst = 15000; // 初回学習ステータス読み込みの待ち時間（ミリ秒）
	var statInterval = 10000; // 学習ステータスの読み込み間隔（ミリ秒）
	var lossMax = 1800; // Loss値の想定回数
	var statTest = 0; // POSTテスト用の変数（モック：1、本番環境：0）
	var loadSec = 2000; // ローディング画面テスト用のタイムラグ（本番環境では0に戻す）

	// 変数の用意
	var stepFlg = 0; // 撮影ステップ
	var capDat = []; // 撮影データの保存
	var winW = window.innerWidth;
	var winH = window.innerHeight;

	// 撮影モードの処理
	var cap = function () {
		$("body").addClass("mode-cap-init");
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
			},
			success: function (data) {
				// デバッグ用に時間差で実行
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

	// 学習スタートの処理
	var train = function () {
		$("body").addClass("mode-train");
		// APIに学習スタートリクエスト
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
			},
			success: function (data) {
				// ここに処理
			}
		});
		// パッケージ画像の描画
		for (var i = 0; i < capDat.length; i++) {
			$(".train-images").append("<dd style='background-image:url(" + capDat[i] + ")'></dd>");
			$(".train-images dd:last-child").css({
				top: winH / 2,
				left: winW / 2,
				transitionDelay: i / 10 + "s"
			});
		}
		// 処理待ちエフェクト
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
		// 時間をおいて、学習ステータスを実行
		setTimeout(stat, statFirst);
	};
	$(".cap-done").click(function () {
		train();
		return false;
	});

	// 学習ステータスのPOST処理
	var compFlg = false; // 学習の完了状況
	var statTimer = setInterval(function () {}, 100);
	var statPost = function () {
		if (compFlg) {
			clearInterval(statTimer);
		} else {
			// テスト用にPOSTURLを加工
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
				},
				success: function (data) {
					if (data.status == "complete") {
						compFlg = true;
					}
					lossDat = data.loss;
					statLoss();
					plot(data.embedded);
				}
			});
		}
	}
	var stat = function () {
		$("body").addClass("mode-stat");
		statPost();
		statTimer = setInterval(statPost, statInterval);
	};

	// Lossの描画処理
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
			lossInterval = 10; // 最後は10ms間隔
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

	// 散布図の描画
	var plot = function (data) {
		// 散布図の描画
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
			label[data[i].property.lid] = data[i].property.label; // ラベル用の配列を生成
		}
		for (var i in label) {
			$(".plot-label").append("<dd class=label-" + i + ">" + label[i] + "</dd>");
		}
		// 時間差で描画
		setTimeout(function () {
			$("body").addClass("mode-plot-start");
		}, 100);
	};

	// 処理の開始
	//$.getJSON(capUrl, function (data) {
	//		$("body").addClass("mode-train");
	//		for (var i in data.uris) {
	//			capDat.push(data.uris[i]);
	//		}
	//		train();
	//	});
	//stat();
	cap();

});
