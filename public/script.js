/* Gaston Security — Request Service form
   Email delivery: Web3Forms (access_key in index.html).
   Optional photo + backup copy: Supabase (fill CONFIG below; leave blank to skip). */
(function () {
  "use strict";

  var CONFIG = {
    supabaseUrl: "",      // e.g. "https://xxxx.supabase.co" — blank = photo upload + backup log off
    supabaseKey: "",      // publishable (anon) key
    bucket: "gaston-request-photos",
    table: "gaston_service_requests",
    maxPhotoBytes: 8 * 1024 * 1024
  };

  var form = document.getElementById("request-form");
  if (!form) return;
  var status = document.getElementById("form-status");
  var btn = document.getElementById("submit-btn");
  var photoInput = document.getElementById("f-photo");
  var photoHint = document.getElementById("photo-hint");

  // Carry the QR / ad source through to the email
  var utm = new URLSearchParams(location.search).get("utm_source") || "direct";
  document.getElementById("utm_source").value = utm;

  // Live-but-polite validation: only flag a field once the user has left it
  form.querySelectorAll("input, textarea").forEach(function (el) {
    el.addEventListener("blur", function () { el.classList.add("touched"); });
  });

  if (!CONFIG.supabaseUrl) {
    photoHint.textContent = "Photos coming soon — for now, text one to (901) 730-9691 after you send this.";
    photoInput.disabled = true;
  }

  function setStatus(msg, kind) {
    status.textContent = msg;
    status.className = "status" + (kind ? " " + kind : "");
  }

  function sbHeaders(extra) {
    var h = { apikey: CONFIG.supabaseKey, Authorization: "Bearer " + CONFIG.supabaseKey };
    for (var k in extra) h[k] = extra[k];
    return h;
  }

  function uploadPhoto(file) {
    if (!CONFIG.supabaseUrl || !file) return Promise.resolve("");
    if (file.size > CONFIG.maxPhotoBytes) return Promise.reject(new Error("Photo is over 8 MB."));
    var ext = (file.name.split(".").pop() || "jpg").toLowerCase().replace(/[^a-z0-9]/g, "") || "jpg";
    var path = new Date().toISOString().slice(0, 10) + "/" +
      Math.random().toString(36).slice(2, 10) + "." + ext;
    var url = CONFIG.supabaseUrl + "/storage/v1/object/" + CONFIG.bucket + "/" + path;
    return fetch(url, {
      method: "POST",
      headers: sbHeaders({ "Content-Type": file.type || "application/octet-stream", "x-upsert": "false" }),
      body: file
    }).then(function (r) {
      if (!r.ok) throw new Error("upload failed " + r.status);
      return CONFIG.supabaseUrl + "/storage/v1/object/public/" + CONFIG.bucket + "/" + path;
    });
  }

  function logToSupabase(data) {
    if (!CONFIG.supabaseUrl) return Promise.resolve();
    return fetch(CONFIG.supabaseUrl + "/rest/v1/" + CONFIG.table, {
      method: "POST",
      headers: sbHeaders({ "Content-Type": "application/json", Prefer: "return=minimal" }),
      body: JSON.stringify({
        name: data.name, phone: data.phone, email: data.email || null,
        site_address: data.site_address, description: data.message,
        photo_url: data.photo_url || null, utm_source: utm, user_agent: navigator.userAgent
      })
    }).catch(function () { /* backup only — never block the email */ });
  }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    form.querySelectorAll("input, textarea").forEach(function (el) { el.classList.add("touched"); });
    if (!form.checkValidity()) {
      setStatus("Please fill in the highlighted fields.", "err");
      var bad = form.querySelector(":invalid");
      if (bad) bad.focus();
      return;
    }

    var fd = new FormData(form);
    var data = {};
    fd.forEach(function (v, k) { if (k !== "photo" && k !== "botcheck") data[k] = v; });
    var captcha = fd.get("h-captcha-response");
    if (captcha) data["h-captcha-response"] = captcha;
    if (fd.get("botcheck")) data.botcheck = true; // honeypot tripped — Web3Forms drops it

    btn.disabled = true;
    setStatus("Sending…");
    var photoNote = "";

    uploadPhoto(photoInput.disabled ? null : photoInput.files[0])
      .then(function (photoUrl) {
        if (photoUrl) { data.photo_url = photoUrl; }
      }, function () {
        photoNote = " (The photo didn't attach — text it to (901) 730-9691.)";
      })
      .then(function () {
        // Put everything in one readable email body
        data.message =
          data.message +
          "\n\n— Site: " + data.site_address +
          "\n— Phone: " + data.phone +
          (data.email ? "\n— Email: " + data.email : "") +
          (data.photo_url ? "\n— Photo: " + data.photo_url : "") +
          "\n— Source: " + utm;
        return Promise.all([
          logToSupabase(data),
          fetch("https://api.web3forms.com/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json", Accept: "application/json" },
            body: JSON.stringify(data)
          }).then(function (r) { return r.json(); })
        ]);
      })
      .then(function (results) {
        var res = results[1];
        if (res && res.success) {
          form.reset();
          form.querySelectorAll(".touched").forEach(function (el) { el.classList.remove("touched"); });
          if (window.hcaptcha) { try { window.hcaptcha.reset(); } catch (e) {} }
          setStatus("Sent. We'll call or text you back." + photoNote, "ok");
        } else {
          throw new Error((res && res.message) || "send failed");
        }
      })
      .catch(function (err) {
        var msg = /captcha/i.test(err.message)
          ? "Please complete the “I am human” check and send again."
          : "Couldn't send. Call or text (901) 730-9691 instead.";
        setStatus(msg, "err");
      })
      .finally(function () { btn.disabled = false; });
  });
})();
