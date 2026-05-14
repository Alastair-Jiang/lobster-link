// ==UserScript==
// @name         知到网课自动连播助手
// @namespace    https://jiangdongxu.online/
// @version      1.0.0
// @description  知到(智慧树)网课自动播放、自动下一集、自动跳过弹窗，安心记笔记
// @author       希伯来
// @match        *://*.zhihuishu.com/*
// @match        *://*.zhihuishu.com/*/*
// @match        *://study.zhihuishu.com/*
// @match        *://online.zhihuishu.com/*
// @grant        none
// @run-at       document-idle
// ==/UserScript==

(function () {
  'use strict';

  // ========== 配置 ==========
  const CONFIG = {
    enableAutoPlay: true,        // 自动播放
    enableAutoNext: true,        // 自动下一集
    enableAutoMute: false,       // 自动静音（默认关，方便听课）
    enableSpeedControl: false,    // 倍速控制（默认关）
    speed: 1.0,                  // 播放倍速（1.0 = 原速）
    autoClosePopup: true,        // 自动关闭弹窗/题目提示
    pollInterval: 1500,          // 检测间隔 (ms)
    nextBtnTimeout: 3000,        // 视频结束后等多久点下一集 (ms)
  };

  // ========== 状态 ==========
  let isRunning = false;
  let pollTimer = null;
  let lastVideoSrc = null;
  let panelEl = null;

  // ========== 核心逻辑 ==========

  /**
   * 找到页面上的 video 元素
   */
  function findVideo() {
    // 知到平台可能在 iframe 里放视频
    const videos = document.querySelectorAll('video');
    if (videos.length > 0) return videos[0];

    // 尝试在 iframe 中查找
    const iframes = document.querySelectorAll('iframe');
    for (const iframe of iframes) {
      try {
        const doc = iframe.contentDocument || iframe.contentWindow.document;
        const v = doc.querySelectorAll('video');
        if (v.length > 0) return v[0];
      } catch (e) {
        // 跨域 iframe 无法访问，忽略
      }
    }
    return null;
  }

  /**
   * 尝试播放视频
   */
  function tryPlay(video) {
    if (!video || video.paused === false) return;

    // 多种方式尝试触发播放
    video.play().catch(() => {
      // 某些平台需要用户交互，尝试模拟点击
      video.click();
      video.muted = CONFIG.enableAutoMute;
      video.play().catch(() => {});
    });

    if (CONFIG.enableSpeedControl) {
      video.playbackRate = CONFIG.speed;
    }
  }

  /**
   * 找"下一集"按钮
   */
  function findNextBtn() {
    // 方式1: 通过常见 class名
    const selectors = [
      '.nextBtn', '.next-btn', '.next', '.nextChapter', '.next-chapter',
      '[class*="next"]', '[class*="Next"]',
      '.el-icon-arrow-right', '.icon-next',
      'button:contains("下一集")', 'button:contains("下一节")',
      'button:contains("继续")', 'span:contains("下一集")',
      '.video-next', '.playNext', '.nextVideo',
      '[title*="下一"]', '[title*="next"]',
      'a:contains("下一")',
    ];

    for (const sel of selectors) {
      try {
        const el = document.querySelector(sel);
        if (el && el.offsetParent !== null) return el;
      } catch (e) {}
    }

    // 方式2: 遍历所有 button / a / span，匹配文本
    const keywords = ['下一集', '下一节', '下集', '继续', '下一章', 'next', 'Next'];
    const allElements = document.querySelectorAll('button, a, span, div[role="button"], li');
    for (const el of allElements) {
      const text = (el.textContent || '').trim();
      if (keywords.some(k => text.includes(k)) && el.offsetParent !== null) {
        // 进一步确认不是无关按钮
        if (text.length < 20 && !text.includes('评论') && !text.includes('弹幕')) {
          return el;
        }
      }
    }

    return null;
  }

  /**
   * 关闭弹窗/题目提示
   */
  function closePopups() {
    if (!CONFIG.autoClosePopup) return;

    // 常见关闭按钮
    const closeSelectors = [
      '.popup-close', '.dialog-close', '.modal-close', '.close-btn',
      '.el-dialog__close', '.el-message-box__close',
      '[class*="close"]', '[aria-label="关闭"]', '[aria-label="Close"]',
      '.icon-close', '.icon-guanbi',
    ];

    for (const sel of closeSelectors) {
      try {
        const el = document.querySelector(sel);
        if (el && el.offsetParent !== null) {
          el.click();
          console.log('[知到助手] 关闭弹窗:', sel);
          return;
        }
      } catch (e) {}
    }

    // 检测"知道了"按钮（平台常见确认按钮）
    const knowBtns = document.querySelectorAll('button, span, div');
    for (const btn of knowBtns) {
      const text = (btn.textContent || '').trim();
      if (['知道了', '确定', '好的', '我知道了', '确认'].includes(text)) {
        if (btn.offsetParent !== null) {
          btn.click();
          console.log('[知到助手] 点击确认按钮:', text);
          return;
        }
      }
    }
  }

  /**
   * 检测视频是否播放完毕
   */
  function isVideoEnded(video) {
    if (!video) return false;
    return video.ended || (video.duration > 0 && video.currentTime >= video.duration - 0.5);
  }

  /**
   * 主循环
   */
  function mainLoop() {
    const video = findVideo();

    if (video) {
      // 视频存在：尝试播放
      tryPlay(video);

      // 检查是否播完了
      if (isVideoEnded(video) && CONFIG.enableAutoNext) {
        console.log('[知到助手] 视频播放完毕，寻找下一集...');
        setTimeout(() => {
          const nextBtn = findNextBtn();
          if (nextBtn) {
            console.log('[知到助手] 点击下一集按钮');
            nextBtn.click();
          } else {
            console.log('[知到助手] 未找到下一集按钮，继续检测...');
          }
        }, CONFIG.nextBtnTimeout);
      }
    } else {
      // 没有视频：可能是页面刚加载，或者在其他页面
      // 尝试检测是否在课程列表页，如果是则不做特别处理
    }

    // 自动关闭弹窗
    closePopups();

    // 更新控制面板状态
    updatePanel(video);
  }

  // ========== 控制面板 UI ==========

  function createPanel() {
    panelEl = document.createElement('div');
    panelEl.id = 'zd-helper-panel';
    panelEl.innerHTML = `
      <style>
        #zd-helper-panel {
          position: fixed;
          bottom: 20px;
          right: 20px;
          z-index: 99999;
          background: rgba(30, 30, 40, 0.92);
          color: #eee;
          border-radius: 12px;
          padding: 12px 16px;
          font-size: 13px;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          box-shadow: 0 4px 20px rgba(0,0,0,0.4);
          backdrop-filter: blur(8px);
          min-width: 200px;
          user-select: none;
          transition: opacity 0.3s;
        }
        #zd-helper-panel.minimized {
          min-width: auto;
          padding: 8px 12px;
        }
        #zd-helper-panel .zd-title {
          font-weight: 700;
          font-size: 14px;
          margin-bottom: 8px;
          color: #7ec8e3;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        #zd-helper-panel .zd-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin: 6px 0;
        }
        #zd-helper-panel .zd-row label {
          cursor: pointer;
          color: #bbb;
          font-size: 12px;
        }
        #zd-helper-panel .zd-row input[type="checkbox"] {
          accent-color: #7ec8e3;
          cursor: pointer;
        }
        #zd-helper-panel .zd-row select,
        #zd-helper-panel .zd-row input[type="range"] {
          cursor: pointer;
        }
        #zd-helper-panel .zd-status {
          font-size: 11px;
          color: #4caf50;
          margin-top: 6px;
        }
        #zd-helper-panel .zd-toggle {
          cursor: pointer;
          font-size: 16px;
        }
        #zd-helper-panel button {
          background: #7ec8e3;
          color: #111;
          border: none;
          border-radius: 6px;
          padding: 4px 12px;
          cursor: pointer;
          font-size: 12px;
          font-weight: 600;
          margin-top: 6px;
        }
        #zd-helper-panel button:hover {
          background: #a0d8f0;
        }
      </style>
      <div class="zd-title">
        <span>🎬 知到助手</span>
        <span class="zd-toggle" id="zd-toggle-min">−</span>
      </div>
      <div id="zd-body">
        <div class="zd-row">
          <label><input type="checkbox" id="zd-autoplay" ${CONFIG.enableAutoPlay ? 'checked' : ''}> 自动播放</label>
          <label><input type="checkbox" id="zd-autonext" ${CONFIG.enableAutoNext ? 'checked' : ''}> 自动下一集</label>
        </div>
        <div class="zd-row">
          <label><input type="checkbox" id="zd-automute" ${CONFIG.enableAutoMute ? 'checked' : ''}> 静音播放</label>
          <label><input type="checkbox" id="zd-speed-ctrl"> 倍速</label>
        </div>
        <div class="zd-row" id="zd-speed-row" style="display:none">
          <span style="color:#bbb;font-size:12px">倍速:</span>
          <select id="zd-speed">
            <option value="1.0">1.0x</option>
            <option value="1.25">1.25x</option>
            <option value="1.5">1.5x</option>
            <option value="1.75">1.75x</option>
            <option value="2.0">2.0x</option>
          </select>
        </div>
        <div class="zd-row">
          <label><input type="checkbox" id="zd-closepopup" ${CONFIG.autoClosePopup ? 'checked' : ''}> 自动关弹窗</label>
        </div>
        <div class="zd-status" id="zd-status">✅ 运行中</div>
        <button id="zd-force-next">⏭ 手动跳下一集</button>
      </div>
    `;

    document.body.appendChild(panelEl);

    // 绑定事件
    document.getElementById('zd-autoplay').addEventListener('change', (e) => {
      CONFIG.enableAutoPlay = e.target.checked;
    });
    document.getElementById('zd-autonext').addEventListener('change', (e) => {
      CONFIG.enableAutoNext = e.target.checked;
    });
    document.getElementById('zd-automute').addEventListener('change', (e) => {
      CONFIG.enableAutoMute = e.target.checked;
      const video = findVideo();
      if (video) video.muted = e.target.checked;
    });
    document.getElementById('zd-closepopup').addEventListener('change', (e) => {
      CONFIG.autoClosePopup = e.target.checked;
    });
    document.getElementById('zd-speed-ctrl').addEventListener('change', (e) => {
      CONFIG.enableSpeedControl = e.target.checked;
      document.getElementById('zd-speed-row').style.display = e.target.checked ? 'flex' : 'none';
      const video = findVideo();
      if (video) {
        video.playbackRate = e.target.checked ? parseFloat(document.getElementById('zd-speed').value) : 1.0;
      }
    });
    document.getElementById('zd-speed').addEventListener('change', (e) => {
      CONFIG.speed = parseFloat(e.target.value);
      const video = findVideo();
      if (video) video.playbackRate = CONFIG.speed;
    });
    document.getElementById('zd-force-next').addEventListener('click', () => {
      const nextBtn = findNextBtn();
      if (nextBtn) {
        nextBtn.click();
        console.log('[知到助手] 手动跳转下一集');
      } else {
        alert('未找到下一集按钮');
      }
    });

    // 最小化切换
    document.getElementById('zd-toggle-min').addEventListener('click', () => {
      const body = document.getElementById('zd-body');
      const toggle = document.getElementById('zd-toggle-min');
      if (body.style.display === 'none') {
        body.style.display = 'block';
        toggle.textContent = '−';
        panelEl.classList.remove('minimized');
      } else {
        body.style.display = 'none';
        toggle.textContent = '+';
        panelEl.classList.add('minimized');
      }
    });
  }

  function updatePanel(video) {
    const statusEl = document.getElementById('zd-status');
    if (!statusEl) return;

    if (video && !video.paused) {
      const current = formatTime(video.currentTime);
      const total = formatTime(video.duration);
      statusEl.textContent = `▶ 播放中 ${current} / ${total}`;
      statusEl.style.color = '#4caf50';
    } else if (video && video.paused) {
      statusEl.textContent = '⏸ 已暂停 (尝试自动播放中...)';
      statusEl.style.color = '#ff9800';
    } else {
      statusEl.textContent = '⏳ 等待视频加载...';
      statusEl.style.color = '#9e9e9e';
    }
  }

  function formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '--:--';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  // ========== 启动 & 停止 ==========

  function start() {
    if (isRunning) return;
    isRunning = true;
    console.log('[知到助手] 🚀 自动连播助手已启动');

    // 初始执行一次
    setTimeout(mainLoop, 1000);

    // 定期轮询
    pollTimer = setInterval(mainLoop, CONFIG.pollInterval);
  }

  function stop() {
    isRunning = false;
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
    console.log('[知到助手] ⏹ 已停止');
  }

  // ========== 页面加载完成后启动 ==========
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    initWhenReady();
  } else {
    window.addEventListener('DOMContentLoaded', initWhenReady);
  }

  function initWhenReady() {
    // 等待页面完全渲染
    setTimeout(() => {
      createPanel();
      start();
    }, 2000);
  }

  // ========== URL 变化检测（SPA 页面切换） ==========
  // 知到平台可能用 SPA，切换课程时 URL 变化但不刷新页面
  let lastUrl = location.href;
  new MutationObserver(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      console.log('[知到助手] 检测到页面切换，重新扫描');
    }
  }).observe(document, { subtree: true, childList: true });

  console.log('[知到助手] 脚本已加载，等待页面就绪...');
})();
