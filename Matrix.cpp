#include "Matrix.h"
#include <stdexcept>
#include <algorithm>

void Matrix::allocate() {
    if (rows_ > 0 && cols_ > 0) {
        data_ = new double[rows_ * cols_]();
    } else {
        data_ = nullptr;
    }
}

void Matrix::free() {
    delete[] data_;
    data_ = nullptr;
}



Matrix::Matrix(int rows, int cols) : rows_(rows), cols_(cols), data_(nullptr) {
    if (rows < 0 || cols < 0) {
        throw std::invalid_argument("Matrix: negative dimensions");
    }
    allocate();
}

Matrix::Matrix(int rows, int cols, double fill)
    : rows_(rows), cols_(cols), data_(nullptr) {
    if (rows < 0 || cols < 0) {
        throw std::invalid_argument("Matrix: negative dimensions");
    }
    allocate();
    int total = rows_ * cols_;
    for (int i = 0; i < total; ++i) data_[i] = fill;
}

Matrix::Matrix(const Matrix& other)
    : rows_(other.rows_), cols_(other.cols_), data_(nullptr) {
    allocate();
    int total = rows_ * cols_;
    std::copy(other.data_, other.data_ + total, data_);
}

Matrix& Matrix::operator=(const Matrix& other) {
    if (this == &other) return *this;

    delete[] data_;
    rows_ = other.rows_;
    cols_ = other.cols_;   
    data_ = nullptr;
    allocate();
    int total = rows_ * cols_;
    std::copy(other.data_, other.data_ + total, data_);
    return *this;
}

Matrix::~Matrix() {
    free();
}

double& Matrix::at(int i, int j) {
    if (i < 0 || i >= rows_ || j < 0 || j >= cols_) {
        throw std::out_of_range("Matrix::at: index out of range");
    }
    return data_[i * cols_ + j];
}


const double& Matrix::at(int i, int j) const {
    if (i < 0 || i >= rows_ || j < 0 || j >= cols_) {
        throw std::out_of_range("Matrix::at: index out of range");
    }
    return data_[i * cols_ + j];
}

Matrix& Matrix::operator+=(const Matrix& other) {
    if (rows_ != other.rows_ || cols_ != other.cols_) {
        throw std::invalid_argument("Matrix::operator+=: size mismatch");
    }
    int total = rows_ * cols_;
    for (int i = 0; i < total; ++i) {
        data_[i] += other.data_[i];
    }
    return *this;
}


Matrix operator+(const Matrix& a, const Matrix& b) {
    if (a.rows_ != b.rows_ || a.cols_ != b.cols_) {
        throw std::invalid_argument("operator+: size mismatch");
    }
    Matrix result = a;   
    result += b;         
    return result;
}

Matrix operator*(const Matrix& a, const Matrix& b) {
    if (a.cols_ != b.rows_) {
        throw std::invalid_argument(
            "operator*: incompatible dimensions (a.cols != b.rows)");
    }
    Matrix result(a.rows_, b.cols_);
    const int ar = a.rows_, ac = a.cols_, bc = b.cols_;
    for (int i = 0; i < ar; ++i) {
        for (int k = 0; k < ac; ++k) {
            const double aik = a.data_[i * ac + k];
            for (int j = 0; j < bc; ++j) {
                result.data_[i * bc + j] += aik * b.data_[k * bc + j];
            }
        }
    }
    return result;
}

std::ostream& operator<<(std::ostream& os, const Matrix& m) {
    os << m.rows_ << ' ' << m.cols_ << '\n';
    for (int i = 0; i < m.rows_; ++i) {
        for (int j = 0; j < m.cols_; ++j) {
            os << m.data_[i * m.cols_ + j];
            if (j + 1 < m.cols_) os << ' ';
        }
        os << '\n';
    }
    return os;
}

std::istream& operator>>(std::istream& is, Matrix& m) {
    int r, c;
    if (!(is >> r >> c)) return is;
    if (r < 0 || c < 0) {
        is.setstate(std::ios::failbit);
        return is;
    }
    Matrix tmp(r, c);
    for (int i = 0; i < r; ++i) {
        for (int j = 0; j < c; ++j) {
            if (!(is >> tmp.data_[i * c + j])) return is;
        }
    }
    m = tmp;
    return is;
}