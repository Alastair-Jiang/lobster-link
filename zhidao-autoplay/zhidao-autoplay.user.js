// ==UserScript==
// @name         知到网课自动连播助手
// @namespace    https://jiangdongxu.online/
// @version      1.3.0
// @description  知到(智慧树)静默自动连播，无日志无面板，安心记笔记
// @author       希伯来
// @include      *://*.zhihuishu.com/*
// @include      *://studyvideoh5.zhihuishu.com/*
// @grant        none
// @run-at       document-idle
// ==/UserScript==

(function () {
  'use strict';

  // ========== 配置 ==========
  const CONFIG = {
    enableAutoPlay: true,
    enableAutoNext: true,
    enableAutoMute: false,
    enableSpeedControl: false,
    speed: 1.0,
    autoClosePopup: true,
    pollInterval: 1500,
    nextBtnTimeout: 3000,
    popupPollInterval: 3000,
  };

  // ========== 状态 ==========
  let isRunning = false;
  let pollTimer = null;

  // ========== 运行指示器（极简，绕过文本检测） ==========
  function showIndicator() {
    const d = document.createElement('div');
    d.style.cssText = 'position:fixed;bottom:4px;right:4px;width:5px;height:5px;border-radius:50%;background:rgba(76,175,80,0.3);z-index:99999;pointer-events:none';
    d.id = '_zda_ind';
    document.body.appendChild(d);
  }

  // ========== 核心逻辑 ==========
  function findVideo() {
    const videos = document.querySelectorAll('video');
    if (videos.length > 0) return videos[0];
    const iframes = document.querySelectorAll('iframe');
    for (const iframe of iframes) {
      try {
        const doc = iframe.contentDocument || iframe.contentWindow.document;
        const v = doc.querySelectorAll('video');
        if (v.length > 0) return v[0];
      } catch (e) {}
    }
    return null;
  }

  function tryPlay(video) {
    if (!video || !video.paused) return;
    video.play().catch(() => {
      video.click();
      video.muted = CONFIG.enableAutoMute;
      video.play().catch(() => {});
    });
    if (CONFIG.enableSpeedControl && video.playbackRate !== CONFIG.speed) {
      video.playbackRate = CONFIG.speed;
    }
  }

  function findNextBtn() {
    const selectors = [
      '.nextBtn', '.next-btn', '.next', '.nextChapter', '.next-chapter',
      '[class*="next"]', '[class*="Next"]',
      '.el-icon-arrow-right', '.icon-next',
      '.video-next', '.playNext', '.nextVideo',
      '[title*="下一"]', '[title*="next"]',
    ];
    for (const sel of selectors) {
      try {
        const el = document.querySelector(sel);
        if (el && el.offsetParent !== null) {
          const text = (el.textContent || '').trim();
          if (text.length < 20 && !text.includes('评论') && !text.includes('弹幕')) return el;
        }
      } catch (e) {}
    }
    const keywords = ['下一集', '下一节', '下集', '继续', '下一章', 'next'];
    const allElements = document.querySelectorAll('button, a, span, div[role="button"], li');
    for (const el of allElements) {
      const text = (el.textContent || '').trim();
      if (text.length < 20 && keywords.some(k => text.includes(k)) && el.offsetParent !== null) {
        return el;
      }
    }
    return null;
  }

  function closePopups() {
    if (!CONFIG.autoClosePopup) return;
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
          return;
        }
      } catch (e) {}
    }
    const knowTexts = ['知道了', '确定', '好的', '我知道了', '确认'];
    const btns = document.querySelectorAll('button, span, div');
    for (const btn of btns) {
      const text = (btn.textContent || '').trim();
      if (knowTexts.includes(text) && btn.offsetParent !== null) {
        btn.click();
        return;
      }
    }
  }

  function isVideoEnded(video) {
    if (!video || !video.duration) return false;
    return video.ended || video.currentTime >= video.duration - 0.5;
  }

  function mainLoop() {
    if (!CONFIG.enableAutoPlay && !CONFIG.enableAutoNext && !CONFIG.autoClosePopup) return;
    const video = findVideo();
    if (video) {
      tryPlay(video);
      if (isVideoEnded(video) && CONFIG.enableAutoNext) {
        setTimeout(() => {
          const nextBtn = findNextBtn();
          if (nextBtn) nextBtn.click();
        }, CONFIG.nextBtnTimeout);
      }
    }
  }

  function closeLoop() {
    if (!CONFIG.autoClosePopup) return;
    closePopups();
  }

  function start() {
    if (isRunning) return;
    isRunning = true;
    setTimeout(mainLoop, 1000);
    pollTimer = setInterval(mainLoop, CONFIG.pollInterval);
    setInterval(closeLoop, CONFIG.popupPollInterval);
    showIndicator();
  }

  function stop() {
    isRunning = false;
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
    const ind = document.getElementById('_zda_ind');
    if (ind) ind.remove();
  }

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(start, 1500);
  } else {
    window.addEventListener('DOMContentLoaded', () => setTimeout(start, 1500));
  }

  // SPA 路由切换重新扫描
  let lastUrl = location.href;
  new MutationObserver(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      stop();
      setTimeout(start, 2000);
    }
  }).observe(document, { subtree: true, childList: true });
})();
