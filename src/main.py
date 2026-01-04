from flask import Flask, request, jsonify
import os
import sys
import traceback

app = Flask(__name__)

# GLOBAL ERROR LOG
STARTUP_ERRORS = []

# WRAPPED IMPORTS to prevent 502 Crash
try:
    from binance_real_handler import handle_real_binance_order
except Exception as e:
    STARTUP_ERRORS.append(f"Binance REAL Import Fail: {str(e)}\n{traceback.format_exc()}")
    def handle_real_binance_order(data): return {"status": "error", "message": "Binance Real Handler Crashed on Load"}

try:
    from flattrade_handler import handle_flattrade_order
except Exception as e:
    STARTUP_ERRORS.append(f"Flattrade Import Fail: {str(e)}\n{traceback.format_exc()}")
    def handle_flattrade_order(data): return {"status": "error", "message": "Flattrade Handler Crashed on Load"}

try:
    from binance_handler import handle_binance_order
except ImportError:
    try:
        from binance_handler_fix import handle_binance_order
    except Exception as e:
        STARTUP_ERRORS.append(f"Binance TEST Import Fail: {str(e)}\n{traceback.format_exc()}")
        def handle_binance_order(data): return {"status": "error", "message": "Binance Test Handler Crashed on Load"}


@app.route('/')
def home():
    status = "Healthy" if not STARTUP_ERRORS else "Degraded"
    return jsonify({
        "status": status,
        "startup_errors": STARTUP_ERRORS,
        "message": "Unified Trading Bot V2.0 (Self-Diagnostic Mode)"
    }), 200

@app.route('/debug')
def debug_logs():
    """Endpoint to view internal import errors"""
    return "<pre>" + "\n\n".join(STARTUP_ERRORS) + "</pre>" if STARTUP_ERRORS else "No Startup Errors."

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No JSON data"}), 400
        
        broker = data.get('broker', 'BINANCE').upper()
        print(f"Received Signal: {broker}")
        
        if broker == 'FLATTRADE':
            return jsonify(handle_flattrade_order(data))
        elif broker == 'BINANCE_REAL':
            return jsonify(handle_real_binance_order(data))
        else:
            return jsonify(handle_binance_order(data))
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
