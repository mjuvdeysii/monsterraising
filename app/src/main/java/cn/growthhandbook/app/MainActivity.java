package cn.growthhandbook.app;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.app.DownloadManager;
import android.database.Cursor;
import android.provider.Settings;
import java.io.File;
import org.json.JSONArray;
import android.print.PrintAttributes;
import android.print.PrintDocumentAdapter;
import android.print.PrintManager;
import android.view.HapticFeedbackConstants;
import android.view.View;
import android.view.ViewTreeObserver;
import android.view.Window;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import org.json.JSONObject;
import java.net.HttpURLConnection;
import java.net.URL;

import androidx.webkit.WebViewAssetLoader;

/** The handbook, bundled inside the app and served from a fixed https origin so that ticks and the birth date persist. */
public class MainActivity extends Activity {
    static final String ORIGIN = "https://appassets.androidplatform.net";
    static final String HOME = ORIGIN + "/assets/site/index.html";
    private WebView web;
    private volatile boolean pageReady = false;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        web = new WebView(this);
        setContentView(web);
        final View content = findViewById(android.R.id.content);
        content.getViewTreeObserver().addOnPreDrawListener(new ViewTreeObserver.OnPreDrawListener() {
            @Override public boolean onPreDraw() {
                if (!pageReady) return false;
                content.getViewTreeObserver().removeOnPreDrawListener(this);
                return true;
            }
        });
        content.postDelayed(() -> { pageReady = true; content.invalidate(); }, 3000);
        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setTextZoom(getSharedPreferences("hb", MODE_PRIVATE).getInt("zoom", 100));
        s.setMediaPlaybackRequiresUserGesture(true);
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);
        web.addJavascriptInterface(new Bridge(this), "HBApp");
        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return loader.shouldInterceptRequest(request.getUrl());
            }
            @Override
            public void onPageFinished(WebView view, String url) {
                if (!pageReady) { pageReady = true; findViewById(android.R.id.content).invalidate(); }
            }
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri u = request.getUrl();
                if (u.toString().startsWith(ORIGIN)) return false;
                try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception ignored) { }
                return true;
            }
        });
        if (state != null) web.restoreState(state);
        else web.loadUrl(target(getIntent()));
    }

    String pendingLog = "";

    private String target(Intent i) {
        if (i != null && "journal".equals(i.getStringExtra("page"))) return HOME + "#journal";
        String lg = i == null ? null : i.getStringExtra("log");
        if (lg != null && !lg.isEmpty()) { pendingLog = lg; return HOME + "#journal"; }
        int m = i == null ? -1 : i.getIntExtra("month", -1);
        return m >= 0 ? HOME + "#m" + m + "-care" : HOME;
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        if ("journal".equals(intent.getStringExtra("page")) && web != null) { web.evaluateJavascript("location.hash='journal'", null); return; }
        String lg = intent.getStringExtra("log");
        if (lg != null && lg.matches("[a-z]+") && web != null) { web.evaluateJavascript("window.HB_LOG&&HB_LOG('" + lg + "')", null); return; }
        int m = intent.getIntExtra("month", -1);
        if (m >= 0 && web != null) web.evaluateJavascript("location.hash='m" + m + "-care'", null);
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @Override
    public void onBackPressed() {
        if (web != null && web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }

    void printSheet() {
        runOnUiThread(() -> {
            PrintManager pm = (PrintManager) getSystemService(Context.PRINT_SERVICE);
            PrintDocumentAdapter inner = web.createPrintDocumentAdapter("养小怪兽一页纸");
            PrintDocumentAdapter adapter = new PrintDocumentAdapter() {
                @Override public void onStart() { inner.onStart(); }
                @Override public void onLayout(PrintAttributes o, PrintAttributes n, android.os.CancellationSignal c, LayoutResultCallback cb, Bundle b) { inner.onLayout(o, n, c, cb, b); }
                @Override public void onWrite(android.print.PageRange[] p, android.os.ParcelFileDescriptor d, android.os.CancellationSignal c, WriteResultCallback cb) { inner.onWrite(p, d, c, cb); }
                @Override public void onFinish() {
                    inner.onFinish();
                    web.evaluateJavascript("document.body.classList.remove('print-sheet')", null);
                }
            };
            pm.print("养小怪兽一页纸", adapter, new PrintAttributes.Builder().setMediaSize(PrintAttributes.MediaSize.ISO_A4).build());
        });
    }

    void applyBars(boolean dark) {
        Window w = getWindow();
        int bar = dark ? 0xFF171513 : 0xFFFFFDF8, nav = dark ? 0xFF211E1B : 0xFFFFFFFF;
        w.setStatusBarColor(bar);
        w.setNavigationBarColor(nav);
        View d = w.getDecorView();
        int f = d.getSystemUiVisibility();
        int light = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | (Build.VERSION.SDK_INT >= 26 ? View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR : 0);
        d.setSystemUiVisibility(dark ? (f & ~light) : (f | light));
        web.setBackgroundColor(bar);
    }

    void shareText(String title, String text) {
        runOnUiThread(() -> {
            Intent i = new Intent(Intent.ACTION_SEND);
            i.setType("text/plain");
            i.putExtra(Intent.EXTRA_SUBJECT, title);
            i.putExtra(Intent.EXTRA_TEXT, text);
            try { startActivity(Intent.createChooser(i, "分享给家人")); } catch (Exception ignored) { }
        });
    }

    // records backup: the person picks where the file goes and which file comes back, through the system file picker
    private static final int SAVE = 21, OPEN = 22;
    private String pendingSave = null;

    void saveFile(String name, String text) {
        runOnUiThread(() -> {
            pendingSave = text;
            Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);
            i.setType("application/json");
            i.putExtra(Intent.EXTRA_TITLE, name);
            try { startActivityForResult(i, SAVE); } catch (Exception e) { pendingSave = null; js("HB_FILE_DONE('save',false)"); }
        });
    }

    void openFile() {
        runOnUiThread(() -> {
            Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);
            i.setType("*/*");
            try { startActivityForResult(i, OPEN); } catch (Exception e) { js("HB_FILE_DONE('open',false)"); }
        });
    }

    private void js(String code) { if (web != null) web.evaluateJavascript(code, null); }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        super.onActivityResult(req, res, data);
        if (req == INSTALL_PERM) {
            if (Build.VERSION.SDK_INT < 26 || getPackageManager().canRequestPackageInstalls()) install(); else js("HB_DL({s:'denied'})");
            return;
        }
        Uri u = (res == RESULT_OK && data != null) ? data.getData() : null;
        if (req == SAVE) {
            String text = pendingSave; pendingSave = null;
            boolean ok = false;
            if (u != null && text != null) {
                try (OutputStream o = getContentResolver().openOutputStream(u, "wt")) { o.write(text.getBytes(StandardCharsets.UTF_8)); ok = true; } catch (Exception ignored) { }
            }
            js("HB_FILE_DONE('save'," + (u == null ? "null" : String.valueOf(ok)) + ")");
        } else if (req == OPEN) {
            if (u == null) { js("HB_FILE_DONE('open',null)"); return; }
            try (InputStream in = getContentResolver().openInputStream(u)) {
                ByteArrayOutputStream b = new ByteArrayOutputStream(); byte[] buf = new byte[8192]; int n; long total = 0;
                while ((n = in.read(buf)) > 0) { b.write(buf, 0, n); total += n; if (total > 2_000_000) throw new Exception("too large"); }
                js("HB_IMPORT(" + JSONObject.quote(b.toString("UTF-8")) + ")");
            } catch (Exception e) { js("HB_FILE_DONE('open',false)"); }
        }
    }

    // update check: reads the latest release on GitHub; nothing about the person is sent
    static final String RELEASES = "https://api.github.com/repos/mjuvdeysii/monsterraising/releases/latest";

    int versionCode() {
        try { return (int) (Build.VERSION.SDK_INT >= 28 ? getPackageManager().getPackageInfo(getPackageName(), 0).getLongVersionCode() : getPackageManager().getPackageInfo(getPackageName(), 0).versionCode); }
        catch (Exception e) { return 0; }
    }

    void checkUpdate(final boolean manual) {
        new Thread(() -> {
            String result;
            try {
                HttpURLConnection c = (HttpURLConnection) new URL(RELEASES).openConnection();
                c.setConnectTimeout(8000); c.setReadTimeout(8000);
                c.setRequestProperty("Accept", "application/vnd.github+json");
                c.setRequestProperty("User-Agent", "growth-handbook-android");
                if (c.getResponseCode() != 200) throw new Exception("http " + c.getResponseCode());
                ByteArrayOutputStream b = new ByteArrayOutputStream();
                try (InputStream in = c.getInputStream()) { byte[] buf = new byte[8192]; int n; while ((n = in.read(buf)) > 0) b.write(buf, 0, n); }
                JSONObject r = new JSONObject(b.toString("UTF-8"));
                String tag = r.optString("tag_name", "");
                int latest = Integer.parseInt(tag.replaceAll("^.*\\.", ""));
                JSONObject out = new JSONObject();
                out.put("current", versionCode());
                out.put("latest", latest);
                out.put("tag", tag);
                out.put("notes", r.optString("body", ""));
                out.put("page", r.optString("html_url", ""));
                if (r.optJSONArray("assets") != null && r.getJSONArray("assets").length() > 0) {
                    JSONObject a0 = r.getJSONArray("assets").getJSONObject(0);
                    out.put("url", a0.optString("browser_download_url", ""));
                    out.put("size", a0.optLong("size", 0));
                }
                out.put("manual", manual);
                result = "HB_UPDATE(" + out.toString() + ")";
            } catch (Exception e) {
                result = manual ? "HB_UPDATE(null)" : "";
            }
            final String code = result;
            if (!code.isEmpty()) runOnUiThread(() -> js(code));
        }).start();
    }

    // in-app update download: the system download service (resumes after network drops), several sources,
    // a source that stops moving is dropped for the next one; the installer opens when the file is complete
    private static final int INSTALL_PERM = 23;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private JSONArray dlUrls; private int dlIndex; private long dlId = -1, dlLastBytes = -1, dlLastMove; private String dlName;

    void downloadUpdate(String urlsJson, String name) {
        runOnUiThread(() -> {
            try { dlUrls = new JSONArray(urlsJson); } catch (Exception e) { js("HB_DL({s:'fail'})"); return; }
            dlName = name; dlIndex = 0; startDownload();
        });
    }

    private void startDownload() {
        DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
        if (dlId >= 0) { dm.remove(dlId); dlId = -1; }
        if (dlUrls == null || dlIndex >= dlUrls.length()) { js("HB_DL({s:'fail'})"); return; }
        File f = new File(getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), dlName);
        if (f.exists()) f.delete();
        try {
            DownloadManager.Request r = new DownloadManager.Request(Uri.parse(dlUrls.getString(dlIndex)));
            r.setTitle(getString(R.string.app_name) + " 更新");
            r.setDescription(dlName);
            r.setMimeType("application/vnd.android.package-archive");
            r.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            r.setDestinationInExternalFilesDir(this, Environment.DIRECTORY_DOWNLOADS, dlName);
            dlId = dm.enqueue(r);
        } catch (Exception e) { dlIndex++; startDownload(); return; }
        dlLastBytes = -1; dlLastMove = System.currentTimeMillis();
        js("HB_DL({s:'run',p:0,src:" + dlIndex + "})");
        ui.postDelayed(this::pollDownload, 700);
    }

    private void pollDownload() {
        if (dlId < 0) return;
        DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
        int status = -1; long done = 0, total = -1;
        try (Cursor c = dm.query(new DownloadManager.Query().setFilterById(dlId))) {
            if (c != null && c.moveToFirst()) {
                status = c.getInt(c.getColumnIndexOrThrow(DownloadManager.COLUMN_STATUS));
                done = c.getLong(c.getColumnIndexOrThrow(DownloadManager.COLUMN_BYTES_DOWNLOADED_SO_FAR));
                total = c.getLong(c.getColumnIndexOrThrow(DownloadManager.COLUMN_TOTAL_SIZE_BYTES));
            }
        } catch (Exception ignored) { }
        long now = System.currentTimeMillis();
        if (status == DownloadManager.STATUS_SUCCESSFUL) { js("HB_DL({s:'done'})"); install(); return; }
        if (status == DownloadManager.STATUS_FAILED || status == -1) { dlIndex++; js("HB_DL({s:'switch'})"); startDownload(); return; }
        if (done != dlLastBytes) { dlLastBytes = done; dlLastMove = now; }
        long limit = done > 0 ? 25000 : 15000;
        if (now - dlLastMove > limit) { dlIndex++; js("HB_DL({s:'switch'})"); startDownload(); return; }
        int pct = total > 0 ? (int) (done * 100 / total) : 0;
        js("HB_DL({s:'run',p:" + pct + "})");
        ui.postDelayed(this::pollDownload, 700);
    }

    private void install() {
        if (Build.VERSION.SDK_INT >= 26 && !getPackageManager().canRequestPackageInstalls()) {
            js("HB_DL({s:'perm'})");
            try { startActivityForResult(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:" + getPackageName())), INSTALL_PERM); } catch (Exception ignored) { }
            return;
        }
        DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
        Uri u = dm.getUriForDownloadedFile(dlId);
        if (u == null) { js("HB_DL({s:'fail'})"); return; }
        Intent i = new Intent(Intent.ACTION_VIEW);
        i.setDataAndType(u, "application/vnd.android.package-archive");
        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
        try { startActivity(i); } catch (Exception e) { js("HB_DL({s:'fail'})"); }
    }

    void cancelDownload() {
        runOnUiThread(() -> { if (dlId >= 0) ((DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE)).remove(dlId); dlId = -1; dlUrls = null; });
    }

    void openUrl(String url) {
        runOnUiThread(() -> { try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); } catch (Exception ignored) { } });
    }

    void askNotificationPermission() {
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            runOnUiThread(() -> requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 7));
        }
    }

    /** Methods the page calls as window.HBApp.* */
    static class Bridge {
        private final MainActivity a;
        Bridge(MainActivity a) { this.a = a; }

        @JavascriptInterface
        public void print() { a.printSheet(); }

        @JavascriptInterface
        public void share(String title, String text) { a.shareText(title, text); }

        @JavascriptInterface
        public void saveFile(String name, String text) { a.saveFile(name, text); }

        // hand a file straight to WeChat, mail or another app, without saving it somewhere first
        @JavascriptInterface
        public void shareFile(String name, String text) {
            try {
                java.io.File dir = new java.io.File(a.getCacheDir(), "share");
                dir.mkdirs();
                java.io.File f = new java.io.File(dir, (name == null ? "file.txt" : name).replace("/", "-"));
                try (java.io.FileOutputStream o = new java.io.FileOutputStream(f)) { o.write((text == null ? "" : text).getBytes("UTF-8")); }
                android.net.Uri uri = androidx.core.content.FileProvider.getUriForFile(a, a.getPackageName() + ".files", f);
                Intent i = new Intent(Intent.ACTION_SEND).setType(f.getName().endsWith(".csv") ? "text/csv" : "application/json")
                        .putExtra(Intent.EXTRA_STREAM, uri).addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                a.runOnUiThread(() -> a.startActivity(Intent.createChooser(i, "发送给")));
            } catch (Exception e) {
                a.runOnUiThread(() -> a.js("HB_FILE_DONE&&HB_FILE_DONE('save',false)"));
            }
        }

        @JavascriptInterface
        public void openFile() { a.openFile(); }

        @JavascriptInterface
        public int version() { return a.versionCode(); }

        @JavascriptInterface
        public String versionName() { try { return a.getPackageManager().getPackageInfo(a.getPackageName(), 0).versionName; } catch (Exception e) { return ""; } }

        @JavascriptInterface
        public void setJournalReminders(String json) {
            Reminders.saveJournal(a, json);
            Reminders.schedule(a);
            if (json != null && json.length() > 2) a.askNotificationPermission();
        }

        @JavascriptInterface
        public void checkUpdate(boolean manual) { a.checkUpdate(manual); }

        @JavascriptInterface
        public void downloadUpdate(String urlsJson, String name) { a.downloadUpdate(urlsJson, name); }

        @JavascriptInterface
        public void cancelDownload() { a.cancelDownload(); }

        @JavascriptInterface
        public void openUrl(String url) { if (url != null && url.startsWith("https://")) a.openUrl(url); }

        @JavascriptInterface
        public void setDark(boolean dark) { a.runOnUiThread(() -> a.applyBars(dark)); }

        @JavascriptInterface
        public void haptic() {
            a.runOnUiThread(() -> a.web.performHapticFeedback(Build.VERSION.SDK_INT >= 30 ? HapticFeedbackConstants.CONFIRM : HapticFeedbackConstants.VIRTUAL_KEY));
        }

        @JavascriptInterface
        public int getTextZoom() { return a.getSharedPreferences("hb", MODE_PRIVATE).getInt("zoom", 100); }

        @JavascriptInterface
        public void setTextZoom(int z) {
            final int v = Math.max(80, Math.min(160, z));
            a.getSharedPreferences("hb", MODE_PRIVATE).edit().putInt("zoom", v).apply();
            a.runOnUiThread(() -> a.web.getSettings().setTextZoom(v));
        }

        @JavascriptInterface
        public void setBirth(String birth) { AgeWidget.saveBirth(a, birth); }

        @JavascriptInterface
        public void setName(String name) { AgeWidget.saveName(a, name); }

        @JavascriptInterface
        public void setJournal(String json) { AgeWidget.saveJournal(a, json); }

        // the chosen look: the widget pictures follow it, and the home-screen icon too when asked
        @JavascriptInterface
        public void setIp(String ip, boolean icon) {
            String look = "eye".equals(ip) ? "eye" : "mint";
            a.getSharedPreferences(AgeWidget.PREFS, MODE_PRIVATE).edit().putString("ip", look).apply();
            AgeWidget.refresh(a);
            boolean eye = icon && "eye".equals(look);
            android.content.pm.PackageManager pm = a.getPackageManager();
            android.content.ComponentName cm = new android.content.ComponentName(a, MainActivity.class.getPackage().getName() + ".IconMint"), ce = new android.content.ComponentName(a, MainActivity.class.getPackage().getName() + ".IconEye");
            int on = android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_ENABLED, off = android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_DISABLED;
            boolean eyeNow = pm.getComponentEnabledSetting(ce) == on;
            if (eye == eyeNow) return;
            pm.setComponentEnabledSetting(eye ? ce : cm, on, android.content.pm.PackageManager.DONT_KILL_APP);
            pm.setComponentEnabledSetting(eye ? cm : ce, off, android.content.pm.PackageManager.DONT_KILL_APP);
        }

        @JavascriptInterface
        public String pendingLog() { String p = a.pendingLog; a.pendingLog = ""; return p == null ? "" : p; }

        @JavascriptInterface
        public void setReminders(String json) {
            Reminders.save(a, json);
            Reminders.schedule(a);
            AgeWidget.refresh(a);
            if (json != null && json.length() > 2) a.askNotificationPermission();
        }
    }
}
