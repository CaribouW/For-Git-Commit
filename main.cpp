#include<iostream>
using namespace std;

int main(int argc, char const *argv[])
{
    const int c = 111;
    int * q =const_cast<int*> (&c);
    *q = 110;
    cout << &c <<"\t"<< c << endl;
    cout << q << "\t"<< *q << endl;
    cout << &c <<"\t"<< c << endl;
    return 0;
}
