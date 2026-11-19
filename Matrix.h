#pragma once
#include <iostream>

class Matrix{
private:
    int rows_ = 0;
    int cols_ = 0;
    double *data_ = nullptr;

    void allocate();
    void free();

public:
    Matrix() = default;
    Matrix(int rows, int cols);
    Matrix(int rows, int cols, double fillValue);
    Matrix (const Matrix& other);
    Matrix& operator=(const Matrix& other);
    ~Matrix();
    
    int rows() const { return rows_; }
    int cols() const { return cols_; }

    double& at(int i, int j);
    const double& at(int i, int j) const;

    Matrix& operator+=(const Matrix& other);

    friend Matrix operator+(const Matrix& a, const Matrix& b);
    friend Matrix operator*(const Matrix& a, const Matrix& b);

    friend std::ostream& operator<<(std::ostream& os, const Matrix& m);
    friend std::istream& operator>>(std::istream& is, Matrix& m);
};