package com.doblepantalla

import android.graphics.BitmapFactory
import android.os.Bundle
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import okio.ByteString
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class MainActivity : AppCompatActivity() {

    private lateinit var image: ImageView
    private lateinit var status: TextView
    private var webSocket: WebSocket? = null

    private val client by lazy {
        OkHttpClient.Builder()
            .readTimeout(0, TimeUnit.MILLISECONDS)
            .pingInterval(15, TimeUnit.SECONDS)
            .build()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContentView(R.layout.activity_main)

        image = findViewById(R.id.screenView)
        status = findViewById(R.id.statusText)

        val url = intent.getStringExtra(EXTRA_URL)
        if (url.isNullOrBlank()) {
            finish()
            return
        }

        setStatus("conectando…")
        connect(url)
        wireTouch()
    }

    private fun wireTouch() {
        image.setOnTouchListener { v, e ->
            val w = v.width.toFloat().coerceAtLeast(1f)
            val h = v.height.toFloat().coerceAtLeast(1f)
            val nx = (e.x / w).coerceIn(0f, 1f)
            val ny = (e.y / h).coerceIn(0f, 1f)
            when (e.actionMasked) {
                MotionEvent.ACTION_DOWN -> send("down", nx, ny)
                MotionEvent.ACTION_MOVE -> send("move", nx, ny)
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> send("up", nx, ny)
                else -> { /* ignore */ }
            }
            true
        }
    }

    private fun connect(url: String) {
        val req = Request.Builder().url(url).build()
        webSocket = client.newWebSocket(req, object : WebSocketListener() {
            override fun onOpen(ws: WebSocket, response: Response) {
                setStatus(null)
            }

            override fun onMessage(ws: WebSocket, bytes: ByteString) {
                val data = bytes.toByteArray()
                val bmp = BitmapFactory.decodeByteArray(data, 0, data.size) ?: return
                runOnUiThread { image.setImageBitmap(bmp) }
            }

            override fun onClosed(ws: WebSocket, code: Int, reason: String) {
                setStatus("desconectado")
            }

            override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
                setStatus("error: ${t.message ?: "desconocido"}")
            }
        })
    }

    private fun send(type: String, x: Float, y: Float) {
        val msg = JSONObject()
            .put("type", type)
            .put("x", x.toDouble())
            .put("y", y.toDouble())
        webSocket?.send(msg.toString())
    }

    private fun setStatus(text: String?) {
        runOnUiThread {
            if (text == null) {
                status.visibility = View.GONE
            } else {
                status.visibility = View.VISIBLE
                status.text = text
            }
        }
    }

    override fun onDestroy() {
        webSocket?.close(1000, "bye")
        webSocket = null
        super.onDestroy()
    }

    companion object {
        const val EXTRA_URL = "url"
    }
}
