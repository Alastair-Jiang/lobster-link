// ==UserScript==
// @name         知到网课自动连播助手
// @namespace    https://jiangdongxu.online/
// @version      1.2.0
// @description  知到(智慧树)静默自动连播，无面板无检测，安心记笔记
// @author       希伯来
// @include      *://*.zhihuishu.com/*
// @include      *://studyvideoh5.zhihuishu.com/*
// @grant        none
// @run-at       document-idle
// ==/UserScript==

(function () {
  'use strict';

  console.log('%c[知到助手] 📦 脚本已加载', 'color:#ff9800;font-weight:bold');

  // ========== 配置 ==========
  const CONFIG = {
    enableAutoPlay: true,        // 自动播放
    enableAutoNext: true,        // 自动下一集
    enableAutoMute: false,       // 自动静音
    enableSpeedControl: false,   // 倍速控制（默认关）
    speed: 1.0,                  // 倍速
    autoClosePopup: true,        // 自动关闭弹窗
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

  // ========== 键盘快捷键 ==========
  // 所有控制通过快捷键，不在页面注入任何 UI，避免被检测
  function setupKeyboard() {
    document.addEventListener('keydown', (e) => {
      // Ctrl+Shift+1: 切换自动播放
      if (e.ctrlKey && e.shiftKey && e.key === '1') {
        e.preventDefault();
        CONFIG.enableAutoPlay = !CONFIG.enableAutoPlay;
        console.log('[知到助手] 自动播放:', CONFIG.enableAutoPlay ? '✅ ON' : '❌ OFF');
      }
      // Ctrl+Shift+2: 切换自动下一集
      if (e.ctrlKey && e.shiftKey && e.key === '2') {
        e.preventDefault();
        CONFIG.enableAutoNext = !CONFIG.enableAutoNext;
        console.log('[知到助手] 自动下一集:', CONFIG.enableAutoNext ? '✅ ON' : '❌ OFF');
      }
      // Ctrl+Shift+3: 手动跳下一集
      if (e.ctrlKey && e.shiftKey && e.key === '3') {
        e.preventDefault();
        const nextBtn = findNextBtn();
        if (nextBtn) {
          nextBtn.click();
          console.log('[知到助手] ⏭ 手动跳转下一集');
        } else {
          console.log('[知到助手] ⚠ 未找到下一集按钮');
        }
      }
      // Ctrl+Shift+4: 切换自动关弹窗
      if (e.ctrlKey && e.shiftKey && e.key === '4') {
        e.preventDefault();
        CONFIG.autoClosePopup = !CONFIG.autoClosePopup;
        console.log('[知到助手] 自动关弹窗:', CONFIG.autoClosePopup ? '✅ ON' : '❌ OFF');
      }
      // Ctrl+Shift+0: 开关全部功能
      if (e.ctrlKey && e.shiftKey && e.key === '0') {
        e.preventDefault();
        const allOn = CONFIG.enableAutoPlay || CONFIG.enableAutoNext || CONFIG.autoClosePopup;
        CONFIG.enableAutoPlay = !allOn;
        CONFIG.enableAutoNext = !allOn;
        CONFIG.autoClosePopup = !allOn;
        console.log('[知到助手] 全部功能:', !allOn ? '✅ ON' : '❌ OFF');
      }
      // Ctrl+Shift+↑: 加速 0.25x
      if (e.ctrlKey && e.shiftKey && e.key === 'ArrowUp') {
        e.preventDefault();
        CONFIG.speed = Math.min(2.0, CONFIG.speed + 0.25);
        CONFIG.enableSpeedControl = true;
        const video = findVideo();
        if (video) video.playbackRate = CONFIG.speed;
        console.log('[知到助手] 倍速:', CONFIG.speed + 'x');
      }
      // Ctrl+Shift+↓: 减速 0.25x
      if (e.ctrlKey && e.shiftKey && e.key === 'ArrowDown') {
        e.preventDefault();
        CONFIG.speed = Math.max(0.5, CONFIG.speed - 0.25);
        if (CONFIG.speed <= 1.0) CONFIG.enableSpeedControl = false;
        const video = findVideo();
        if (video) video.playbackRate = CONFIG.speed;
        console.log('[知到助手] 倍速:', CONFIG.speed + 'x');
      }
      // Ctrl+Shift+M: 切换静音
      if (e.ctrlKey && e.shiftKey && e.key === 'M') {
        e.preventDefault();
        CONFIG.enableAutoMute = !CONFIG.enableAutoMute;
        const video = findVideo();
        if (video) video.muted = CONFIG.enableAutoMute;
        console.log('[知到助手] 静音:', CONFIG.enableAutoMute ? '🔇 ON' : '🔊 OFF');
      }
    });
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
    setTimeout(() => {
      setupKeyboard();
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

  console.log('%c[知到助手] 🎬 静默模式已就绪 %c| 快捷键: Ctrl+Shift+1-4 控制各项 | Ctrl+Shift+0 全部开关', 'color:#7ec8e3;font-weight:bold', 'color:#999');
  console.log('%c[知到助手] 自动播放=✅ | 自动下一集=✅ | 自动关弹窗=✅', 'color:#4caf50');
})();
