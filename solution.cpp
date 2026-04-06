#include <iostream>
#include <vector>

template <typename T>
class IHeap {
public:
    virtual ~IHeap() = default;
    virtual void push(const T& val) = 0;
    virtual T top() const = 0;
    virtual void pop() = 0;
    virtual int size() const = 0;
    virtual bool empty() const = 0;
};

template <typename T, typename Comp>
class Heap : public IHeap<T> {
    std::vector<T> data;
    Comp comp;

    void siftUp(int i) {
        while (i > 0) {
            int p = (i - 1) / 2;
            if (comp(data[i], data[p])) {
                T tmp = data[i]; data[i] = data[p]; data[p] = tmp;
                i = p;
            } else break;
        }
    }

    void siftDown(int i) {
        int n = (int)data.size();
        while (2 * i + 1 < n) {
            int best = 2 * i + 1;
            if (best + 1 < n && comp(data[best + 1], data[best]))
                best++;
            if (comp(data[best], data[i])) {
                T tmp = data[i]; data[i] = data[best]; data[best] = tmp;
                i = best;
            } else break;
        }
    }

public:
    void push(const T& val) override {
        data.push_back(val);
        siftUp((int)data.size() - 1);
    }

    T top() const override { return data[0]; }

    void pop() override {
        data[0] = data.back();
        data.pop_back();
        if (!data.empty()) siftDown(0);
    }

    int size() const override { return (int)data.size(); }
    bool empty() const override { return data.empty(); }
};

struct Less { bool operator()(long long a, long long b) { return a < b; } };
struct Greater { bool operator()(long long a, long long b) { return a > b; } };

int main() {
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int n;
    std::cin >> n;

    Heap<long long, Greater> maxHeap;
    Heap<long long, Less> minHeap;

    for (int i = 0; i < n; i++) {
        long long w;
        std::cin >> w;

        if (maxHeap.empty() || w <= maxHeap.top())
            maxHeap.push(w);
        else
            minHeap.push(w);

        if (maxHeap.size() > minHeap.size() + 1) {
            minHeap.push(maxHeap.top());
            maxHeap.pop();
        } else if (minHeap.size() > maxHeap.size()) {
            maxHeap.push(minHeap.top());
            minHeap.pop();
        }

        long long median;
        if (maxHeap.size() > minHeap.size())
            median = maxHeap.top();
        else
            median = (maxHeap.top() + minHeap.top()) / 2;

        std::cout << median << '\n';
    }

    return 0;
}
