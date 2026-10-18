package cn.growthhandbook.app;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.print.PrintAttributes;
import android.print.PrintDocumentAdapter;
import android.print.PrintManager;
import android.view.HapticFeedbackConstants;
import android.view.View;
import android.view.Window;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.webkit.WebViewAssetLoader;

/** The handbook, bundled inside the app and served from a fixed https origin so that ticks and the birth date persist. */
public class MainActivity extends Activity {
    static final String ORIGIN = "https://appassets.androidplatform.net";
    static final String HOME = ORIGIN + "/assets/site/index.html";
    private WebView web;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        web = new WebView(this);
        setContentView(web);
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

    private String target(Intent i) {
        int m = i == null ? -1 : i.getIntExtra("month", -1);
        return m >= 0 ? HOME + "#m" + m + "-care" : HOME;
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
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
            PrintDocumentAdapter inner = web.createPrintDocumentAdapter("成长手册一页纸");
            PrintDocumentAdapter adapter = new PrintDocumentAdapter() {
                @Override public void onStart() { inner.onStart(); }
                @Override public void onLayout(PrintAttributes o, PrintAttributes n, android.os.CancellationSignal c, LayoutResultCallback cb, Bundle b) { inner.onLayout(o, n, c, cb, b); }
                @Override public void onWrite(android.print.PageRange[] p, android.os.ParcelFileDescriptor d, android.os.CancellationSignal c, WriteResultCallback cb) { inner.onWrite(p, d, c, cb); }
                @Override public void onFinish() {
                    inner.onFinish();
                    web.evaluateJavascript("document.body.classList.remove('print-sheet')", null);
                }
            };
            pm.print("成长手册一页纸", adapter, new PrintAttributes.Builder().setMediaSize(PrintAttributes.MediaSize.ISO_A4).build());
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
        public void setReminders(String json) {
            Reminders.save(a, json);
            Reminders.schedule(a);
            if (json != null && json.length() > 2) a.askNotificationPermission();
        }
    }
}
