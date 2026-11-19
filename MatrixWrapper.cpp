#include "Matrix.h"

#include <string>
#include <cstring>
#include <sstream>
#include <exception>
#include <algorithm>

#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT __attribute__((visibility("default")))
#endif

static thread_local std::string g_last_error;

extern "C" {
    EXPORT const char* matrix_last_error(){
        return g_last_error.c_str();
    }

    EXPORT void* matrix_create(int rows, int cols) {
        try {
            g_last_error.clear();
            return static_cast<void*> (new Matrix(rows, cols));
        } catch (const std::exception& e) {
            g_last_error = e.what();
            return nullptr;
        }
    }

    EXPORT void* matrix_create_filled(int rows, int cols, double fill) {
        try {
            g_last_error.clear();
            return static_cast<void*>(new Matrix(rows, cols, fill));
        } catch (const std::exception& e) {
            g_last_error = e.what();
            return nullptr;
        }
    }

    EXPORT void matrix_destroy(void* ptr) {
        delete static_cast<Matrix*>(ptr);
    }

    EXPORT void* matrix_clone(void* src_ptr){
        try {
            g_last_error.clear();
            const Matrix* src = static_cast<const Matrix*>(src_ptr);
            return static_cast<void*>(new Matrix(*src));
        } catch (const std::exception& e) {
            g_last_error = e.what();
            return nullptr;
        }
    }

    EXPORT int matrix_rows(void* ptr) {
        if (!ptr) { g_last_error = "null pointer"; return -1; }
        return static_cast<Matrix*>(ptr)->rows();
    }

    EXPORT int matrix_cols(void* ptr) {
        if (!ptr) { g_last_error = "null pointer"; return -1; }
        return static_cast<Matrix*>(ptr)->cols();
    }

    EXPORT int matrix_get_element(void* ptr , int i, int j, double* out) {
        try
        {
            g_last_error.clear();
            if (!ptr || !out) { g_last_error = "null pointer"; return -1; }
            *out = static_cast<Matrix*>(ptr)->at(i, j);
            return 0;
        } catch(const std::exception& e)
        {
            g_last_error = e.what();
            return -1;
        }
    }

    EXPORT int matrix_set_element(void* ptr, int i, int j, double value) {
        try {
            g_last_error.clear();
            if (!ptr) { g_last_error = "null pointer"; return -1; }
            static_cast<Matrix*>(ptr)->at(i, j) = value;
            return 0;
        } catch (const std::exception& e) {
            g_last_error = e.what();
            return -1;
        }
    }

    EXPORT int matrix_copy_to(void* ptr, double* out_data, int out_size) {
        try {
            g_last_error.clear();
            if (!ptr || !out_data) { g_last_error = "null pointer"; return -1; }
            Matrix* m = static_cast<Matrix*>(ptr);
            const int total = m->rows() * m->cols();
            if (out_size < total) {
                g_last_error = "buffer too small in matrix_copy_to";
                return -2;
            }
            for (int i = 0; i < m->rows(); ++i)
                for (int j = 0; j < m->cols(); ++j)
                    out_data[i * m->cols() + j] = m->at(i, j);
            return 0;
        } catch (const std::exception& e) {
            g_last_error = e.what();
            return -1;
        }
    }

    EXPORT int matrix_copy_from(void* ptr, const double* in_data, int in_size) {
        try {
            g_last_error.clear();
            if (!ptr || !in_data) { g_last_error = "null pointer"; return -1; }
            Matrix* m = static_cast<Matrix*>(ptr);
            const int total = m->rows() * m->cols();
            if (in_size != total) {
                g_last_error = "size mismatch in matrix_copy_from";
                return -2;
            }
            for (int i = 0; i < m->rows(); ++i)
                for (int j = 0; j < m->cols(); ++j)
                    m->at(i, j) = in_data[i * m->cols() + j];
            return 0;
        } catch (const std::exception& e) {
            g_last_error = e.what();
            return -1;
        }
    }

    EXPORT void* matrix_add(void* a_ptr, void* b_ptr) {
        try {
            g_last_error.clear();
            Matrix* a = static_cast<Matrix*>(a_ptr);
            Matrix* b = static_cast<Matrix*>(b_ptr);
            if (!a || !b) { g_last_error = "null pointer"; return nullptr; }
            return static_cast<void*>(new Matrix((*a) + (*b)));
        } catch (const std::exception& e) {
            g_last_error = e.what();
            return nullptr;
        }
    }

    EXPORT void* matrix_multiply(void* a_ptr, void* b_ptr) {
        try {
            g_last_error.clear();
            Matrix* a = static_cast<Matrix*>(a_ptr);
            Matrix* b = static_cast<Matrix*>(b_ptr);
            if (!a || !b) { g_last_error = "null pointer"; return nullptr; }
            return static_cast<void*>(new Matrix((*a) * (*b)));
        } catch (const std::exception& e) {
            g_last_error = e.what();
            return nullptr;
        }
    }

    EXPORT int matrix_add_assign(void* a_ptr, void* b_ptr) {
        try {
            g_last_error.clear();
            Matrix* a = static_cast<Matrix*>(a_ptr);
            Matrix* b = static_cast<Matrix*>(b_ptr);
            if (!a || !b) { g_last_error = "null pointer"; return -1; }
            (*a) += (*b);
            return 0;
        } catch (const std::exception& e) {
            g_last_error = e.what();
            return -1;
        }
    }

    EXPORT int matrix_to_string(void* ptr, char* out_buf, int buf_size) {
        try {
            g_last_error.clear();
            if (!ptr) { g_last_error = "null pointer"; return -1; }
            std::ostringstream oss;
            oss << *static_cast<Matrix*>(ptr);
            const std::string s = oss.str();
            const int required = static_cast<int>(s.size()) + 1;
            if (buf_size > 0 && out_buf) {
                const int copy_len = std::min<int>(s.size(), buf_size - 1);
                std::memcpy(out_buf, s.data(), copy_len);
                out_buf[copy_len] = '\0';
            }
            return required;
        } catch (const std::exception& e) {
            g_last_error = e.what();
            return -1;
        }
    }
}