"""
Debug Helpers for Docassemble Development
Provides enhanced error reporting and debugging utilities
"""

import sys
import traceback
import json
from docassemble.base.util import log, get_config, user_info

class DebugHelper:
    """Enhanced debugging utilities for docassemble interviews"""
    
    @staticmethod
    def capture_error():
        """Capture and format current exception details"""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if not exc_type:
            return None
            
        error_info = {
            'type': exc_type.__name__,
            'message': str(exc_value),
            'traceback': traceback.format_tb(exc_traceback),
            'formatted_exception': traceback.format_exc(),
            'line_number': None,
            'file_name': None,
            'function_name': None
        }
        
        # Extract specific error location
        if exc_traceback:
            tb_frame = traceback.extract_tb(exc_traceback)[-1]
            error_info['line_number'] = tb_frame.lineno
            error_info['file_name'] = tb_frame.filename
            error_info['function_name'] = tb_frame.name
            
        return error_info
    
    @staticmethod
    def log_error(error_info=None, context=""):
        """Log error details for debugging"""
        if not error_info:
            error_info = DebugHelper.capture_error()
            
        if error_info:
            log(f"ERROR in {context}: {error_info['type']} - {error_info['message']}", 'error')
            log(f"Location: {error_info['file_name']}:{error_info['line_number']}", 'error')
            log(f"Traceback: {error_info['formatted_exception']}", 'error')
            
        return error_info
    
    @staticmethod
    def safe_execute(func, *args, **kwargs):
        """Safely execute a function and capture any errors"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = DebugHelper.capture_error()
            DebugHelper.log_error(error_info, f"safe_execute: {func.__name__}")
            return {'error': True, 'error_info': error_info, 'result': None}
    
    @staticmethod
    def validate_yaml_variables(*variable_names):
        """Check if required variables are defined"""
        undefined = []
        for var_name in variable_names:
            try:
                # Try to access the variable in the global scope
                eval(var_name)
            except NameError:
                undefined.append(var_name)
                
        if undefined:
            error_msg = f"Undefined variables: {', '.join(undefined)}"
            log(error_msg, 'error')
            raise NameError(error_msg)
            
        return True
    
    @staticmethod
    def get_session_debug_info():
        """Get current session debugging information"""
        try:
            info = user_info()
            return {
                'session_id': info.session if hasattr(info, 'session') else 'unknown',
                'filename': info.filename if hasattr(info, 'filename') else 'unknown',
                'user': info.user if hasattr(info, 'user') else 'unknown',
                'question_id': info.question.id if hasattr(info, 'question') and hasattr(info.question, 'id') else 'unknown'
            }
        except:
            return {
                'session_id': 'error',
                'filename': 'error',
                'user': 'error',
                'question_id': 'error'
            }
    
    @staticmethod
    def format_error_display(error_info):
        """Format error information for display in interview"""
        if not error_info:
            return "No error information available"
            
        session_info = DebugHelper.get_session_debug_info()
        
        html = f"""
        <div style="background-color: #fee; border: 2px solid #c00; padding: 15px; margin: 10px 0; border-radius: 5px;">
            <h3 style="color: #c00;">⚠️ Error Detected</h3>
            
            <div style="background-color: #fff; padding: 10px; margin: 10px 0; border-left: 4px solid #c00;">
                <strong>Error Type:</strong> <code>{error_info.get('type', 'Unknown')}</code><br/>
                <strong>Message:</strong> <code>{error_info.get('message', 'No message')}</code><br/>
                <strong>Location:</strong> <code>{error_info.get('file_name', 'unknown')}:{error_info.get('line_number', '?')}</code><br/>
                <strong>Function:</strong> <code>{error_info.get('function_name', 'unknown')}</code>
            </div>
            
            <details>
                <summary style="cursor: pointer; color: #00c;"><strong>Full Traceback</strong></summary>
                <pre style="background-color: #f5f5f5; padding: 10px; overflow-x: auto;">
{error_info.get('formatted_exception', 'No traceback available')}
                </pre>
            </details>
            
            <details>
                <summary style="cursor: pointer; color: #00c;"><strong>Session Information</strong></summary>
                <div style="background-color: #f5f5f5; padding: 10px;">
                    <strong>Session ID:</strong> {session_info['session_id']}<br/>
                    <strong>Interview File:</strong> {session_info['filename']}<br/>
                    <strong>Question ID:</strong> {session_info['question_id']}<br/>
                    <strong>User:</strong> {session_info['user']}
                </div>
            </details>
        </div>
        """
        
        return html

# Convenience functions for direct import
def debug_error():
    """Capture and return current error details"""
    return DebugHelper.capture_error()

def log_debug_error(context=""):
    """Log current error with context"""
    return DebugHelper.log_error(context=context)

def show_error():
    """Return formatted HTML error display"""
    error_info = DebugHelper.capture_error()
    return DebugHelper.format_error_display(error_info)

def check_variables(*vars):
    """Validate that variables are defined"""
    return DebugHelper.validate_yaml_variables(*vars)